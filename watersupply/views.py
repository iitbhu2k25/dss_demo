from django.shortcuts import render
from django.http import JsonResponse
from waterdemands.models import PopulationData, PopulationDataYear, FloatingData

def main_page(request):
    return render(request, 'watersupply/main.html')

# Fetch State, district, subdistrict and villages
def get_locations(request):
    """Fetch hierarchical location data."""
    state_code = request.GET.get("state_code")
    district_code = request.GET.get("district_code")
    subdistrict_code = request.GET.get("subdistrict_code")
    village_code = request.GET.get("village_code")

    if not state_code:
        # Fetch all unique states
        locations = PopulationData.objects.filter(district_code=0, subdistrict_code=0, village_code=0)
        location_list = [{"code": loc.state_code, "name": loc.region_name} for loc in locations]
        return JsonResponse(location_list, safe=False)

    elif state_code and not district_code:
        # Fetch districts within the given state
        locations = PopulationData.objects.filter(state_code=state_code, subdistrict_code=0, village_code=0)
        location_list = [
            {"code": loc.district_code, "name": " ALL" if loc.district_code == 0 else loc.region_name} 
            for loc in locations
        ]
        return JsonResponse(location_list, safe=False)

    elif state_code and district_code and not subdistrict_code:
        # Fetch subdistricts within the given state and district
        locations = PopulationData.objects.filter(state_code=state_code, district_code=district_code, village_code=0)
        location_list = [
            {"code": loc.subdistrict_code, "name": " ALL" if loc.subdistrict_code == 0 else loc.region_name} 
            for loc in locations
        ]
        return JsonResponse(location_list, safe=False)

    elif state_code and district_code and subdistrict_code:
        # Fetch villages within the given state, district, and subdistrict
        locations = PopulationData.objects.filter(
            state_code=state_code, district_code=district_code, subdistrict_code=subdistrict_code
        )
        location_list = [{"code": loc.village_code, "name": loc.region_name} for loc in locations]
        return JsonResponse(location_list, safe=False)

    elif state_code and district_code and subdistrict_code and village_code:
        # Fetch the population of the selected village for 2011
        try:
            village_population_2011 = PopulationData.objects.filter(
                state_code=state_code,
                district_code=district_code,
                subdistrict_code=subdistrict_code,
                village_code=village_code
            ).values_list('population_2011', flat=True).first()
            print("village_population_2011:", village_population_2011)
            if village_population_2011 is None:
                return JsonResponse({"error": "Population data not found for the selected village."}, status=404)

            return JsonResponse({"village_population_2011": village_population_2011}, safe=False)
        

        except PopulationData.DoesNotExist:
            return JsonResponse({"error": "Village not found."}, status=404)
        

    # Invalid request
    return JsonResponse({"error": "Invalid parameters or hierarchy."}, status=400)



