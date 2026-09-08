import json
import os
import urllib.error
import urllib.request


class FiveMBLL:

    @staticmethod
    def sync_player_job(discord_id, job, grade):
        url = os.getenv("FIVEM_BRIDGE_URL")
        token = os.getenv("FIVEM_BRIDGE_TOKEN")

        if not url:
            return {
                "success": False,
                "status": "not_configured",
                "message": "FIVEM_BRIDGE_URL não configurado."
            }

        if not token:
            return {
                "success": False,
                "status": "not_configured",
                "message": "FIVEM_BRIDGE_TOKEN não configurado."
            }

        endpoint = url.rstrip("/") + "/api/discord/job"

        payload = {
            "discord_id": str(discord_id),
            "job": str(job),
            "grade": int(grade)
        }

        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            endpoint,
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-MW-Token": token
            }
        )

        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                response_data = response.read().decode("utf-8")

                return json.loads(response_data)

        except urllib.error.HTTPError as error:
            try:
                response_data = error.read().decode("utf-8")
                return json.loads(response_data)
            except Exception:
                return {
                    "success": False,
                    "status": "http_error",
                    "message": f"HTTP {error.code}"
                }

        except urllib.error.URLError as error:
            return {
                "success": False,
                "status": "connection_error",
                "message": str(error.reason)
            }

        except Exception as error:
            return {
                "success": False,
                "status": "error",
                "message": str(error)
            }