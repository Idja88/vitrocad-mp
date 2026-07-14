from dotenv import load_dotenv
import os
from api.vitro_cad_api import VitroCADAPIClient

load_dotenv()


def update_counter():
    """Update counters value in counter list."""

    counter_list_id = os.getenv("VITRO_CAD_COUNTER_LIST_ID")
    counter_id_list = os.getenv("VITRO_CAD_COUNTER_ITEM_ID_LIST")
    counter_value = os.getenv("VITRO_CAD_COUNTER_VALUE")

    if counter_id_list:
        counter_id_list = [
            cid.strip() for cid in counter_id_list.split(",") if cid.strip()
        ]
    else:
        counter_id_list = []

    # Initialize client
    client = VitroCADAPIClient()

    try:
        for counter_id in counter_id_list:
            data = {
                "list_id": counter_list_id,
                "id": counter_id,
                "counter": counter_value,
            }

            response = client.update_mp_list(data)

            if response:
                print(f"Counter updated successfully for item {counter_id}")
            else:
                print(f"Failed to update counter for item {counter_id}")

    finally:
        client.close()


if __name__ == "__main__":
    update_counter()
