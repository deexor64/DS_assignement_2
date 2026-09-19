from zeep import Client


def run():
    client = Client("http://localhost:8000/?wsdl")

    print("\n--- 1. Reporting Hazard (Valid) ---")
    res1 = client.service.ReportHazard("Flooding", "Water level rising", "Colombo")
    print(res1)

    print("\n--- 2. Fetching Status (Valid) ---")
    res2 = client.service.GetHazardStatus(res1.hazard_id)
    print(res2)

    print("\n--- 3. Listing Hazards by Region (Valid) ---")
    res3 = client.service.ListHazards("Colombo")
    print(res3)

    print("\n--- 4. Testing Input Validation Error Mapping ---")
    try:
        # Intentionally missing the required Region to trigger gRPC validation
        client.service.ReportHazard("Missing Region", "Desc", "")
    except Exception as e:
        print(f"SOAP Fault Caught: {e}")


if __name__ == "__main__":
    run()
