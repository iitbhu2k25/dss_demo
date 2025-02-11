from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import os
import csv,json,math
import pandas as pd
from django.views.decorators.csrf import csrf_exempt
from waterdemands.models import PopulationData,PopulationDataYear



def prediction_methods_page(request):
  return render(request,"population/prediction_methods.html")

def time_series_based_page(request):
  return render(request,"population/time_series_based.html")


def scenario_based_page(request):
  return render(request,"population/scenario_based.html")


def cohort_component_based_page(request):
  return render(request,"population/cohort_component_based.html")

def demographic_based_page(request):
    return render(request,"population/demographic_based.html")


def get_states(request):
    # Filter states (state_code > 0, others == 0)
    states = PopulationData.objects.filter(
        district_code=0,
        subdistrict_code=0,
        village_code=0
    ).order_by('region_name').values('state_code', 'region_name')
    
    # Return JSON response
    return JsonResponse(list(states), safe=False)

def get_districts(request, state_code):
    # Filter districts where subdistrict_code and village_code are 0
    locations = PopulationData.objects.filter(
        state_code=state_code,
        subdistrict_code=0,
        village_code=0
    )

    # Generate district list with 'ALL' for district_code == 0
    district_list = [
        {"district_code": loc.district_code, "region_name": " All " if loc.district_code == 0 else loc.region_name}
        for loc in locations
    ]

    # Sort alphabetically by region_name and then numerically by district_code
    district_list.sort(key=lambda x: (x["region_name"], x["district_code"]))

    return JsonResponse(district_list, safe=False)


def get_subdistricts(request, state_code, district_code):
    # Filter subdistricts where village_code is 0
    locations = PopulationData.objects.filter(
        state_code=state_code,
        district_code=district_code,
        village_code=0
    )

    # Generate subdistrict list with 'ALL' for subdistrict_code == 0
    subdistrict_list = [
        {"subdistrict_code": loc.subdistrict_code, "region_name": " All " if loc.subdistrict_code == 0 else loc.region_name}
        for loc in locations
    ]

    # Sort alphabetically by region_name and then numerically by subdistrict_code
    subdistrict_list.sort(key=lambda x: (x["region_name"], x["subdistrict_code"]))

    return JsonResponse(subdistrict_list, safe=False)

def get_villages(request, state_code, district_code, subdistrict_code):
    # Filter villages based on state, district, and subdistrict codes
    locations = PopulationData.objects.filter(
        state_code=state_code,
        district_code=district_code,
        subdistrict_code=subdistrict_code
    )

    # Generate village list with 'ALL' for village_code == 0
    village_list = [
        {"village_code": loc.village_code, "region_name": " All " if loc.village_code == 0 else loc.region_name, "population_2011": loc.population_2011}
        for loc in locations
    ]

    # Sort so that " All " appears at the top
    village_list.sort(key=lambda x: (x["region_name"] != " All ", x["region_name"], x["village_code"]))

    return JsonResponse(village_list, safe=False)



@csrf_exempt
def calculate_demographic_projection(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            state_code = data.get('state')
            district_code = data.get('district')
            subdistrict_code = data.get('subdistrict')
            villages = data.get('villages', [])
            base_year = data.get('baseYear')
            projection_method = data.get('projectionMethod')
            target_year = data.get('targetYear')
            target_year_range = data.get('targetYearRange')  
            annual_birth_rate = float(data.get('birthRate', 0))
            annual_death_rate = float(data.get('deathRate', 0))
            annual_emigration_rate = float(data.get('emigrationRate', 0))
            annual_immigration_rate = float(data.get('immigrationRate', 0))

            print(f"State = {state_code}")
            print(f"district = {district_code}")
            print(f"subdistrict = {subdistrict_code}")
            print(f"villages = {villages}")
            print(f"base_year = {base_year}")
            print(f"projection_method = {projection_method}")
            print(f"target_year = {target_year}")
            print(f"target_year_range = {target_year_range}")
            print(f"Annual Birth Rate: {annual_birth_rate}")
            print(f"Annual Death Rate: {annual_death_rate}")
            print(f"Annual Emigration Rate: {annual_emigration_rate}")
            print(f"Annual Immigration Rate: {annual_immigration_rate}")



            village_2011_population = {}
          
            if len(villages) > 0: #village-2636726
                village_codes = [int(village.split('-')[1]) for village in villages]
                # Filter the initial queryset for all village codes at once
                query_2011_village_population = PopulationData.objects.filter(
                    state_code=state_code,
                    district_code=district_code,
                    subdistrict_code=subdistrict_code,
                    village_code__in=village_codes  # Use `__in` to filter for multiple values
                )

                # Fetch the data for all matching villages
                data = query_2011_village_population.values('village_code', 'population_2011')

                # Map population data to the respective village codes
                village_2011_population = {item['village_code']: item['population_2011'] for item in data}


            print(f"village_2011_population= {village_2011_population}")
            base_year = int(base_year)
            result = {}
            res={}
            
            if target_year:
                # For a single target year
                target_year = int(target_year)
                for key, value in village_2011_population.items():
                    one_year = {}                      
                    one_year[2011] = value #populating 2011 population of village to result dict
                    t = target_year - base_year
                    for _ in range(1):
                        population_of_target_year = value + (value * t * (annual_birth_rate-annual_death_rate)) + (t * (annual_emigration_rate - annual_immigration_rate))
                        one_year[target_year] = math.floor((population_of_target_year))
                    res[key] = one_year

            elif target_year_range:
                # For a range of target years
                start = int(target_year_range['start'])
                end = int(target_year_range['end'])
                
                for key, value in village_2011_population.items():
                    year_wise_population = {}  # To store population for each year in the range
                    year_wise_population[2011] = value #populating 2011 population of village to result dict
                    for x in range(start, end + 1):
                        t = x - base_year
                        population_of_target_year_range = value + (value * t * (annual_birth_rate-annual_death_rate)) + (t * (annual_emigration_rate - annual_immigration_rate))
                        year_wise_population[x] = int(population_of_target_year_range)
                    res[key] = year_wise_population  # Assign year-wise populations to the village
            
            result['demographic-attribute'] = res
            print(f" result= {result}")
            return JsonResponse({'success': True, 'result': result})
           


        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})    
            
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})



@csrf_exempt
def calculate_projection(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            state_code = data.get('state')
            district_code = data.get('district')
            subdistrict_code = data.get('subdistrict')
            villages = data.get('villages', [])
            base_year = data.get('baseYear')
            projection_method = data.get('projectionMethod')
            target_year = data.get('targetYear')
            target_year_range = data.get('targetYearRange')  
            
            
            print(f"State = {state_code}")
            print(f"district = {district_code}")
            print(f"subdistrict = {subdistrict_code}")
            print(f"villages = {villages}")
            print(f"base_year = {base_year}")
            print(f"projection_method = {projection_method}")
            print(f"target_year = {target_year}")
            print(f"target_year_range = {target_year_range}")
        

            village_2011_population = {}

            if len(villages) > 0: #village-2636726
                village_codes = [int(village.split('-')[1]) for village in villages]
                # Filter the initial queryset for all village codes at once
                query_2011_village_population = PopulationData.objects.filter(
                    state_code=state_code,
                    district_code=district_code,
                    subdistrict_code=subdistrict_code,
                    village_code__in=village_codes  # Use `__in` to filter for multiple values
                )

                # Fetch the data for all matching villages
                data = query_2011_village_population.values('village_code', 'population_2011')

                # Map population data to the respective village codes
                village_2011_population = {item['village_code']: item['population_2011'] for item in data}


            print(f"village_2011_population= {village_2011_population}")
            population_1951_to_2011 =[]
            print(f"Villages_2011_pop {village_2011_population}")
            if state_code and district_code and subdistrict_code:
                query = PopulationDataYear.objects.filter(state_code=state_code,district_code=district_code, subdistrict_code=subdistrict_code)
                data = query.values(
                              'state_code',
                              'district_code',
                              'subdistrict_code',
                              'region_name',
                              'population_1951',
                              'population_1961',
                              'population_1971',
                              'population_1981',
                              'population_1991',
                              'population_2001',
                              'population_2011',
                          )
                if data.exists():  # Check if query returned results
                    # Use the first record from the query
                    record = data[0]
                    population_1951_to_2011.append(record.get('population_1951', None))
                    population_1951_to_2011.append(record.get('population_1961', None))
                    population_1951_to_2011.append(record.get('population_1971', None))
                    population_1951_to_2011.append(record.get('population_1981', None))
                    population_1951_to_2011.append(record.get('population_1991', None))
                    population_1951_to_2011.append(record.get('population_2001', None))
                    population_1951_to_2011.append(record.get('population_2011', None))
                else:
                      print("No data found for the given state, district, and subdistrict codes.")

            print(f"1951 se 2011 {population_1951_to_2011}")
            p1 =  population_1951_to_2011[0]   # 1951 selected subdistrict population
            p2 =  population_1951_to_2011[1]   # 1961 selected subdistrict population
            p3 =  population_1951_to_2011[2]   # 1971 selected subdistrict population
            p4 =  population_1951_to_2011[3]   # 1981 selected subdistrict population
            p5 =  population_1951_to_2011[4]   # 1991 selected subdistrict population
            p6 =  population_1951_to_2011[5]   # 2001 selected subdistrict population
            p7 =  population_1951_to_2011[6]   # 2011 selected subdistrict population
            

            d1 = p2-p1
            d2 = p3-p2
            d3 = p4-p3
            d4 = p5-p4  
            d5 = p6-p5
            d6 = p7-p6
            
            result = {}
            base_year  =int(base_year)
            
            if projection_method == "arithmetic-increase":
              d_mean = (d1+d2+d3+d4+d5+d6) / 6
              annual_growth_rate = d_mean / 10
              annual_growth_rate = math.floor(annual_growth_rate)
              res = {}
              
              
              if target_year:
                  # For a single target year
                  target_year = int(target_year)
                  for key, value in village_2011_population.items():
                      one_year = {}                      
                      one_year[2011] = value #populating 2011 population of village to result dict
                      for _ in range(1):
                          k = value/p7
                          population_of_target_year = value + ((annual_growth_rate * (target_year - base_year)) * (k))
                          one_year[target_year] = math.floor((population_of_target_year))
                      res[key] = one_year

              elif target_year_range:
                  # For a range of target years
                  start = int(target_year_range['start'])
                  end = int(target_year_range['end'])

                  for key, value in village_2011_population.items():
                      year_wise_population = {}  # To store population for each year in the range
                      year_wise_population[2011] = value #populating 2011 population of village to result dict
                      for x in range(start, end + 1):
                          population_of_target_year_range = value + ((annual_growth_rate * (x - base_year)) * (value/p7))
                          year_wise_population[x] = int(population_of_target_year_range)
                      res[key] = year_wise_population  # Assign year-wise populations to the village
              
              result['arithmetic-increase'] = res
              print(f" result= {result}")
                      
                
            elif projection_method == 'geometric-increase':
               # First, let's add error checking for the growth rates
                g1 = (d1 * 100) / p1 if p1 != 0 else 0
                g2 = (d2 * 100) / p2 if p2 != 0 else 0
                g3 = (d3 * 100) / p3 if p3 != 0 else 0
                g4 = (d4 * 100) / p4 if p4 != 0 else 0
                g5 = (d5 * 100) / p5 if p5 != 0 else 0
                g6 = (d6 * 100) / p6 if p6 != 0 else 0
                

                # For the annual growth rate, we need to handle negative or zero values
                growth_values = [g1, g2, g3, g4, g5, g6]
                valid_growth_values = [g for g in growth_values if g > 0]

                if valid_growth_values:
                    # Calculate geometric mean only for positive values
                    product = 1
                    for g in valid_growth_values:
                        product *= g
                    annual_growth_rate = math.pow(product, 1/len(valid_growth_values))
                else:
                    # Handle the case where no valid growth rates exist
                    annual_growth_rate = 0

                # Rest of your code remains the same
                res = {}
                if target_year:
                    # For a single target year
                    target_year = int(target_year)
                    n = (target_year-base_year)/10
                    for key, value in village_2011_population.items():
                        one_year = {}
                        one_year[2011] = value
                        population_of_target_year = value * (math.pow((1 + (annual_growth_rate/100)), n))
                        one_year[target_year] = int(population_of_target_year)
                        res[key] = one_year    

                elif target_year_range:
                    # For a range of target years
                    start = int(target_year_range['start'])
                    end = int(target_year_range['end'])

                    for key, value in village_2011_population.items():
                        year_wise_population = {}
                        year_wise_population[2011] = value
                        for x in range(start, end + 1):
                            n = (x-base_year)/10
                            population_of_target_year_range = value * (math.pow((1 + (annual_growth_rate/100)), n))
                            year_wise_population[x] = int(population_of_target_year_range)
                        res[key] = year_wise_population

                result['geometric-increase'] = res
                


            elif projection_method == 'logistic-growth':
                g1 = (d1) / p1 if p1 != 0 else 0
                g2 = (d2) / p2 if p2 != 0 else 0
                g3 = (d3) / p3 if p3 != 0 else 0
                g4 = (d4) / p4 if p4 != 0 else 0
                g5 = (d5) / p5 if p5 != 0 else 0
                g6 = (d6) / p6 if p6 != 0 else 0

                print(f"Growth rates: g1={g1}, g2={g2}, g3={g3}, g4={g4}, g5={g5}, g6={g6}")
                r1 = math.log(1+g1)
                r2 = math.log(1+g2)
                r3 = math.log(1+g3)
                r4 = math.log(1+g4)
                r5 = math.log(1+g5)
                r6 = math.log(1+g6)
                
                r_mean = (r1 + r2 + r3 + r4 + r5 + r6) / 6
                print(f"Mean growth rate: {r_mean}")
                
                annual_growth_rate = math.exp(r_mean) - 1

                print(f"Annual growth rate: {annual_growth_rate}")

                res = {}
                if target_year:
                    target_year = int(target_year)
                    t = target_year - 1991
                    for key, value in village_2011_population.items():
                        try:
                            print(f"\nProcessing village {key} with 2011 population {value}")
                            if value == 0:
                                continue
                                
                            p_2 = float(value)  # village_2011 population
                            p_0 = p_2 * ((1 - (annual_growth_rate/100))**2)  # 1991
                            p_1 = p_2 * (1 - (annual_growth_rate/100))  # 2001
                            p_1 = round(p_1, 2) 
                            p_0 = round(p_0, 2)
                            
                            print(f"p_0={p_0}, p_1={p_1}, p_2={p_2}")
                            
                            if abs(p_0 * p_2 - p_1**2) < 1e-10:  # Check for near-zero
                                ps = 0
                            else:
                                ps = (2 * p_0 * p_1 * p_2 - p_1**2 * (p_0 + p_2)) / (p_0 * p_2 - p_1**2)
                            print(f"ps={ps}")
                            
                            # Extra safety checks
                            if p_1 <= 0 or p_0 <= 0 or ps <= p_0 or ps <= p_1:
                                print(f"Invalid values detected for logarithm calculation")
                                population_of_target_year = 0
                            else:
                                log_denominator = (p_0 / p_1) * ((ps - p_1) / (ps - p_0))
                                print(f"log_denominator={log_denominator}")
                                
                                if log_denominator <= 0:
                                    print(f"Negative log_denominator")
                                    population_of_target_year = 0
                                else:
                                    n = (2.3/10) * math.log10(log_denominator)  # Using log10 directly
                                    m = (ps - p_0) / p_0
                                    print(f"n={n}, m={m}")
                                    
                                    denominator = 1 + m * math.exp(n*t)
                                    population_of_target_year = ps / denominator if denominator != 0 else 0
                                    print(f"denominator={denominator}, population={population_of_target_year}")
                            
                            one_year = {
                                2011: value,
                                target_year: int(population_of_target_year)
                            }
                            res[key] = one_year
                            
                        except Exception as e:
                            print(f"Error processing village {key}: {str(e)}")
                            one_year = {2011: value, target_year: 0}
                            res[key] = one_year



                elif target_year_range:
                    start = int(target_year_range['start'])
                    end = int(target_year_range['end'])

                    for key, value in village_2011_population.items():
                        if value == 0:
                            continue
                            
                        try:
                            p_2 = float(value)  # village_2011 population
                            p_0 = p_2 * ((1 - (annual_growth_rate/100))**2)  # 1991
                            p_1 = p_2 * (1 - (annual_growth_rate/100))  # 2001
                            p_1 = round(p_1, 2) 
                            p_0 = round(p_0, 2)
                            
                            print(f"p_0={p_0}, p_1={p_1}, p_2={p_2}")
                            
                            if abs(p_0 * p_2 - p_1**2) < 1e-10:  # Check for near-zero
                                ps = 0
                            else:
                                ps = (2 * p_0 * p_1 * p_2 - p_1**2 * (p_0 + p_2)) / (p_0 * p_2 - p_1**2)
                            print(f"ps={ps}")
                            
                            # Check for invalid conditions early
                            if (p_1 == 0 or ps == p_0 or p_0 <= 0 or p_1 <= 0 or ps <= 0):
                                year_wise_population = {2011: value}
                                for x in range(start, end + 1):
                                    year_wise_population[x] = 0
                            else:
                                # Calculate log_denominator safely
                                log_term = (p_0 / p_1) * ((ps - p_1) / (ps - p_0))
                                if log_term <= 0:
                                    year_wise_population = {2011: value}
                                    for x in range(start, end + 1):
                                        year_wise_population[x] = 0
                                else:
                                    n = (2.3/10) * math.log(log_term, 10)
                                    m = (ps - p_0) / p_0 if p_0 != 0 else 0
                                    
                                    year_wise_population = {2011: value}
                                    for x in range(start, end + 1):
                                        try:
                                            t = x - 1991
                                            exp_term = math.exp(n*t)
                                            # Check for overflow in exp calculation
                                            if exp_term == float('inf'):
                                                population = 0
                                            else:
                                                denominator = 1 + m * exp_term
                                                population = ps / denominator if denominator != 0 else 0
                                            year_wise_population[x] = int(population)
                                        except (OverflowError, ValueError):
                                            year_wise_population[x] = 0
                                        
                            res[key] = year_wise_population
                            
                        except (ValueError, ZeroDivisionError):
                            year_wise_population = {2011: value}
                            for x in range(start, end + 1):
                                year_wise_population[x] = 0
                            res[key] = year_wise_population

                result['logistic-growth'] = res
                

               


            elif projection_method == 'incremental-growth':
                d_mean = (d1+d2+d3+d4+d5+d6) / 6

                m1 = d2 - d1
                m2 = d3 - d2
                m3 = d4 - d3
                m4 = d5 - d4
                m5 = d6 - d5 
                m_mean = (m1+m2+m3+m4+m5) / 5

                res = {}
                if target_year:
                    # For a single target year
                    target_year = int(target_year)
                    n = (target_year - base_year) / 10
                    for key, value in village_2011_population.items():
                        k = value / p7
                        one_year = {}
                        one_year[2011] = value #populating 2011 population of village to result dict
                        for _ in range(1):
                            # print(f"n={n}, d_mean = {d_mean}, pop_2011_vill {value}, m_mean {m_mean}, pop_2011_subdis {p7}")
                            population_of_target_year = value + k*n*d_mean + ((n*(n+1))*m_mean / 2)*k
                            one_year[target_year] = int(population_of_target_year)
                        res[key] = one_year

                elif target_year_range:
                    # For a range of target years
                    start = int(target_year_range['start'])
                    end = int(target_year_range['end'])
                    
                    for key, value in village_2011_population.items():
                        year_wise_population = {}  # To store population for each year in the range
                        year_wise_population[2011] = value #populating 2011 population of village to result dict
                        for x in range(start, end + 1):
                            n = (x - base_year) / 10
                            k = value / p7
                            population_of_target_year_range = value + k*n*d_mean + ((n*(n+1))*m_mean / 2)*k
                            year_wise_population[x] = int(population_of_target_year_range)
                        res[key] = year_wise_population  # Assign year-wise populations to the village

                result['incremental-growth'] = res
                

          

            elif projection_method == 'exponential-growth':
                x1 =  1951-base_year
                x2 =   1961-base_year
                x3 =  1971-base_year
                x4 =  1981-base_year
                x5 = 1991-base_year
                x6 = 2001-base_year
                x7 = 2011-base_year

                y1 = math.log(p1,10)
                y2 = math.log(p2, 10)
                y3 = math.log(p3,10)
                y4 = math.log(p4, 10)
                y5 = math.log(p5,10)
                y6 = math.log(p6,10)
                y7 = math.log(p7,10)

                x_i_sum = x1+x2+x3+x4+x5+x6+x7
                y_i_sum = y1+y2+y3+y4+y5+y6+y7
                x_i_square_sum = x1**2 + x2**2 + x3**2 + x4**2 + x5**2 + x6**2 + x7**2
                x_y_prod_sum = x1*y1 + x2*y2 + x3*y3 + x4*y4 + x5*y5 + x6*y6 + x7*y7
                x_sum_prod_y_sum = x_i_sum * y_i_sum

                n = 7

                growth_rate = ((n*x_y_prod_sum) - x_sum_prod_y_sum) / (n*x_i_square_sum - (x_i_sum**2)) # r
                print(f"growth_rate_of_expo {growth_rate}")

                res = {}
                if target_year:
                    # For a single target year
                    target_year = int(target_year)
                    t = target_year - base_year
                    for key, value in village_2011_population.items():
                      one_year = {}
                      one_year[2011] = value  #populating 2011 population of village to result dict
                      for _ in range(1):
                          population_of_target_year =  value * math.exp(growth_rate*t)
                          one_year[target_year] = int(population_of_target_year)
                      res[key] = one_year    

                elif target_year_range:
                    # For a range of target years
                    start = int(target_year_range['start'])
                    end = int(target_year_range['end'])

                    for key, value in village_2011_population.items():
                        year_wise_population = {}  # To store population for each year in the range
                        year_wise_population[2011] = value  #populating 2011 population of village to result dict
                        for x in range(start, end + 1):
                            t = x - base_year
                            population_of_target_year_range = value * math.exp(growth_rate*t)
                            year_wise_population[x] = int(population_of_target_year_range)
                        res[key] = year_wise_population  # Assign year-wise populations to the village
                
                
                result['exponential-growth'] = res
                



            else:
                result = 'Invalid method selected.'

            return JsonResponse({'success': True, 'result': result})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

