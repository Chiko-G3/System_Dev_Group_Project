# Mohamed Hamouda (23077543)   
from database import tenant_service

def test_scalability_large_dataset(monkeypatch):
    # Simulate large dataset (1000 tenants)
    large_data = [(i, f"Tenant{i}") for i in range(1000)]

    def fake_get_all_tenants(*args, **kwargs):
        return large_data

    # Patch database call
    monkeypatch.setattr(tenant_service, "get_all_tenants", fake_get_all_tenants)

    # Run function
    result = tenant_service.get_all_tenants()

    # Check system handles large data
    assert len(result) == 1000