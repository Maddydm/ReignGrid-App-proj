import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import unittest
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import INSPECTOR_EMAIL, INSPECTOR_PASSWORD, LEGACY_INSPECTOR_EMAIL
from backend.database import db

client = TestClient(app)

class TestReignGridBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db.reseed()

    def test_01_dashboard_summary(self):
        """Verify macro KPIs matching Screen 2 Command Center."""
        response = client.get("/api/dashboard/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_parcels"], 1248)
        self.assertEqual(data["verified_parcels"], 1116)
        self.assertEqual(data["needs_review"], 84)
        self.assertEqual(data["discrepancies"], 48)
        self.assertEqual(data["monitored_acres"], 642.8)
        self.assertEqual(data["ai_engine_status"], "ONLINE")

    def test_02_list_parcels(self):
        """Verify listing cadastral parcels with numeric area_sqft and WGS84 geometry."""
        response = client.get("/api/parcels")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 10)
        first = data[0]
        self.assertIn("id", first)
        self.assertIn("owner", first)
        self.assertIn("area_sqft", first)
        self.assertIsInstance(first["area_sqft"], (int, float))
        self.assertIn("registered_geom", first)
        self.assertEqual(first["registered_geom"]["type"], "Polygon")
        self.assertIn("status", first)

    def test_03_get_parcel_detail(self):
        """Verify single parcel detail retrieval with discrepancy info and displacement."""
        response = client.get("/api/parcels/PCL-1044")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], "PCL-1044")
        self.assertEqual(data["status"], "discrepancy")
        self.assertEqual(data["conflict_with"], "PCL-1045")
        self.assertGreater(data["area_sqft"], 20000.0)
        self.assertIsNotNone(data["discrepancy_details"])
        self.assertEqual(data["discrepancy_details"]["displacement_m"], 2.4)

    def test_04_auth_flow(self):
        """Verify inspector login and JWT issuance for both current and legacy emails."""
        # Current email
        resp1 = client.post("/api/auth/login", json={
            "username": INSPECTOR_EMAIL,
            "password": INSPECTOR_PASSWORD
        })
        self.assertEqual(resp1.status_code, 200)
        token = resp1.json()["access_token"]

        # Legacy email
        resp2 = client.post("/api/auth/login", json={
            "username": LEGACY_INSPECTOR_EMAIL,
            "password": INSPECTOR_PASSWORD
        })
        self.assertEqual(resp2.status_code, 200)

        # Profile retrieval
        me_resp = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(me_resp.status_code, 200)
        self.assertEqual(me_resp.json()["role"], "inspector")

    def test_05_discrepancy_center_api(self):
        """Verify Screen 6 Discrepancy Center listing and assignment."""
        login_resp = client.post("/api/auth/login", json={
            "username": INSPECTOR_EMAIL,
            "password": INSPECTOR_PASSWORD
        })
        token = login_resp.json()["access_token"]

        # List discrepancies
        resp = client.get("/api/discrepancies?priority=HIGH")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(any(d["parcel_id"] == "PCL-1044" for d in data))

        # Assign survey
        assign_resp = client.post(
            "/api/discrepancies/DISC-1044/assign",
            json={
                "inspector_name": "Dr. J. Jean Justus",
                "priority": "HIGH",
                "due_date": "2024-11-05",
                "survey_notes": "Verify eastern fence boundary with GNSS RTK receiver."
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(assign_resp.status_code, 200)
        self.assertEqual(assign_resp.json()["status"], "Assigned")

    def test_06_field_verification_workflow(self):
        """Verify Screen 7 Field Verification 5-stage submission."""
        login_resp = client.post("/api/auth/login", json={
            "username": INSPECTOR_EMAIL,
            "password": INSPECTOR_PASSWORD
        })
        token = login_resp.json()["access_token"]

        # List field verifications
        resp = client.get("/api/field-verifications")
        self.assertEqual(resp.status_code, 200)
        fvs = resp.json()
        self.assertTrue(len(fvs) > 0)

        # Submit verification for FV-1044
        sub_resp = client.post(
            "/api/field-verifications/FV-1044/submit",
            json={
                "field_notes": "Boundary stone B-12 located. Discrepancy verified and adjusted.",
                "evidence_photo_url": "https://example.com/marker.jpg",
                "resolution_action": "boundary_verified"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(sub_resp.status_code, 200)
        res = sub_resp.json()
        self.assertEqual(res["status"], "Resolved")
        self.assertEqual(res["current_step"], 5)

        # Verify parcel status updated
        parcel_resp = client.get("/api/parcels/PCL-1044")
        self.assertEqual(parcel_resp.json()["status"], "verified")

    def test_07_ai_pipeline_7_stages(self):
        """Verify 7-stage AI Cadastral Verification execution."""
        login_resp = client.post("/api/auth/login", json={
            "username": INSPECTOR_EMAIL,
            "password": INSPECTOR_PASSWORD
        })
        token = login_resp.json()["access_token"]

        process_resp = client.post(
            "/api/process/img-srm-ramapuram-01",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(process_resp.status_code, 200)
        res = process_resp.json()
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["pipeline_stages"]), 7)
        stage_names = [s["stage"] for s in res["pipeline_stages"]]
        self.assertIn("01_ingestion", stage_names)
        self.assertIn("03_unet_segmentation", stage_names)
        self.assertIn("07_db_sync", stage_names)

    def test_08_discrepancy_report_json_and_pdf(self):
        """Verify ReportLab PDF and JSON generation with REIGNGRID branding."""
        # JSON format
        resp_json = client.get("/api/parcels/PCL-1048/discrepancy-report?format=json")
        self.assertEqual(resp_json.status_code, 200)
        data = resp_json.json()
        self.assertEqual(data["product"], "REIGNGRID")
        self.assertEqual(data["parcel_id"], "PCL-1048")
        self.assertEqual(data["conflict_with"], "PCL-1049")
        self.assertIn("displacement_m", data)

        # PDF format
        resp_pdf = client.get("/api/parcels/PCL-1048/discrepancy-report?format=pdf")
        self.assertEqual(resp_pdf.status_code, 200)
        self.assertEqual(resp_pdf.headers["content-type"], "application/pdf")
        self.assertTrue(resp_pdf.content.startswith(b"%PDF"))
        self.assertIn("REIGNGRID-Report-PCL-1048.pdf", resp_pdf.headers.get("content-disposition", ""))

    def test_09_activity_feed_and_search(self):
        """Verify activity feed and global search."""
        # Activity
        act_resp = client.get("/api/activity")
        self.assertEqual(act_resp.status_code, 200)
        activities = act_resp.json()
        self.assertIsInstance(activities, list)
        self.assertTrue(len(activities) > 0)

        # Search
        search_resp = client.get("/api/search?q=Devika")
        self.assertEqual(search_resp.status_code, 200)
        s_data = search_resp.json()
        self.assertTrue(len(s_data["parcels"]) > 0 or len(s_data["discrepancies"]) > 0)

    def test_10_unauthorized_access(self):
        """Verify protected endpoints reject unauthorized requests."""
        resp1 = client.post("/api/process/img-srm-ramapuram-01")
        self.assertEqual(resp1.status_code, 401)

        resp2 = client.post("/api/discrepancies/DISC-1044/assign", json={})
        self.assertEqual(resp2.status_code, 401)

        resp3 = client.post("/api/field-verifications/FV-1044/submit", json={})
        self.assertEqual(resp3.status_code, 401)

if __name__ == "__main__":
    unittest.main()
