import time

from zeep import Client


def run():
    time.sleep(3)  # Wait for gateway to boot
    client = Client("http://gateway:8000/?wsdl")

    print("--- Reporting Hazard ---")
    res1 = client.service.ReportHazard("Flooding", "Water level rising", "Colombo")
    print(res1)

    print("\n--- Testing Error Mapping (Invalid ID) ---")
    try:
        client.service.GetHazardStatus("invalid-id")
    except Exception as e:
        print(f"SOAP Fault Caught: {e}")


if __name__ == "__main__":
    run()
