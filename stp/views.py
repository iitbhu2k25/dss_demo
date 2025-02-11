from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import render
from .models import Data
import json
import geopandas as gpd
from shapely.geometry import mapping
from .service import weight_redisturb,normalize_data,rank_process 
from shapely.geometry import Polygon, MultiPolygon
from shapely.validation import make_valid
import shapely.ops as ops
def stp_home(request):
    return render(request, 'stp/prediction.html')

@csrf_exempt
def GetStatesView(request):
    states=Data.objects.values('id','name','state','district','subdistrict','village').filter(district=0,subdistrict=0,village=0).distinct()
    print(states)
    return JsonResponse(list(states),safe=False)

@csrf_exempt
def GetDistrictView(request):
    if request.method == 'POST':
        request=json.loads(request.body)
        print("request of dis ",request)
        state = request.get('state') ## fetch the state id
        districts=Data.objects.values('name','id','state','district','subdistrict','village').filter(state=state,subdistrict=0,village=0)
        districts=list(districts)
        state_name=Data.objects.values('name').filter(state=state,subdistrict=0,village=0,district=0)
        new_district=[d for d in districts if d['name']!=state_name[0]['name']]
        new_district.sort(key=lambda x: x['name'])
        return JsonResponse(new_district,safe=False)
@csrf_exempt
def GetSubDistrictView(request):
    if request.method == 'POST':
        request=json.loads(request.body)
        print("request of sub dis",request)
        state=request.get('state')
        district=request.get('district')
        sub_district=Data.objects.values('name','id','state','district','subdistrict','village').filter(state=state,district=district,village=0)
        new_sub_district=[d for d in sub_district if d['subdistrict']!=0]
        new_sub_district.sort(key=lambda x: x['name'])
        print("sub dis",list(new_sub_district))
        return JsonResponse(list(new_sub_district),safe=False)

@csrf_exempt
def  GetVillageView(request):
    if request.method == 'POST':
        request=json.loads(request.body)
        state=request.get('state')
        district=request.get('district')
        sub_district=request.get('sub_district')
        village=Data.objects.values('name','id','state','district','subdistrict','village').filter(state=state,district=district,subdistrict=sub_district)
        new_village=[d for d in village if d['village']!=0]
        new_village.sort(key=lambda x: x['name'])
        print("village",list(new_village))
        return JsonResponse(list(new_village),safe=False)

@csrf_exempt
def GetTableView(request):
    if request.method == 'POST':
        request=json.loads(request.body)
        main_data=request.get('main_data')
        vig_data=main_data['villages']
        table_id=[]
        for i in vig_data:
            table_id.append(int(i[8:]))
        categories=request.get('categories')
        ans=Data.objects.values('name',*categories).filter(id__in=table_id)
        ans=list(ans)
        for i in ans:
            print(i)
        return JsonResponse(ans,safe=False)
    

@csrf_exempt
def GetRankView(request):
    if request.method == 'POST':
        request=json.loads(request.body)
        table_data=request.get('tableData')
        headings=[]
        for i in table_data[0]:
            headings.append(i)        
        headings.remove('name')
        weight_key=weight_redisturb(headings)
        table_data=normalize_data(table_data)
        ans=rank_process(table_data,weight_key,headings)
        print('main ans',ans)
        return JsonResponse(ans,safe=False)

@csrf_exempt
def GetBoundry(request):
    if request.method == 'GET':
        try:
            gdf = gpd.read_file('media/shapefile/all_district/States_Sub_District.shp')
            coordinates = []
            
            for geometry in gdf.geometry:
                if geometry.geom_type == 'Polygon':
                    coords = [[[float(x), float(y)] for x, y in geometry.exterior.coords]]
                    coordinates.extend(coords)
                elif geometry.geom_type == 'MultiPolygon':
                    multi_coords = []
                    for polygon in geometry.geoms:  
                        coords = [[float(x), float(y)] for x, y in polygon.exterior.coords]
                        multi_coords.append(coords)
                    coordinates.extend(multi_coords)
                    
            return JsonResponse({'coordinates': coordinates})
        except Exception as e:
            print(str(e))
            return JsonResponse({'error': str(e)}, status=500)
    if request.method == 'POST':
        try:
            # Read the shapefile
            gdf = gpd.read_file('media/shapefile/all_district/States_Sub_District.shp')
            coordinates = []
            request_data = json.loads(request.body)
            
            def fix_geometry(geometry):
                """Fix invalid geometries and handle topology exceptions"""
                try:
                    # Check if geometry is valid
                    if not geometry.is_valid:
                        # Try to make the geometry valid
                        geometry = make_valid(geometry)
                    
                    # Handle empty geometries
                    if geometry.is_empty:
                        return None
                        
                    # Ensure we have the right geometry type
                    if isinstance(geometry, (Polygon, MultiPolygon)):
                        return geometry
                    else:
                        # If we got a different geometry type, try to convert it
                        return ops.unary_union(geometry)
                        
                except Exception as e:
                    print(f"Error fixing geometry: {str(e)}")
                    return None

            def process_geometry(geometry):
                """Process and extract coordinates from geometry"""
                try:
                    # Fix any topology issues first
                    fixed_geometry = fix_geometry(geometry)
                    if fixed_geometry is None:
                        return
                    
                    if isinstance(fixed_geometry, Polygon):
                        # Process single polygon
                        coords = []
                        # Get exterior coordinates
                        for x, y in fixed_geometry.exterior.coords:
                            coords.append([float(y), float(x)])  # [longitude, latitude]
                        coordinates.append(coords)
                        
                    elif isinstance(fixed_geometry, MultiPolygon):
                        # Process each polygon in the MultiPolygon
                        for polygon in fixed_geometry.geoms:
                            poly_coords = []
                            # Get exterior coordinates for each polygon
                            for x, y in polygon.exterior.coords:
                                poly_coords.append([float(y), float(x)])  # [longitude, latitude]
                            coordinates.append(poly_coords)
                            
                except Exception as e:
                    print(f"Error processing geometry coordinates: {str(e)}")
            
            # Filter data based on request
            try:
                if request_data.get('villages'):
                    village_list = request_data['villages']
                    filtered_gdf = gdf[gdf['village'].isin(village_list)]
                
                elif request_data.get('sub_district'):
                    # Get required parameters
                    sub_district = request_data['sub_district']
                    district = request_data.get('district')
                    state = request_data.get('state')
                    
                    # Build filter conditions
                    conditions = (gdf['sdtname'] == sub_district)
                    if district:
                        conditions &= (gdf['dtname'] == district)
                    if state:
                        conditions &= (gdf['stname'] == state)
                    filtered_gdf = gdf[conditions]
                
                elif request_data.get('district'):
                    # Get required parameters
                    district = request_data['district']
                    state = request_data.get('state')
                    
                    # Build filter conditions
                    conditions = (gdf['dtname'] == district)
                    if state:
                        conditions &= (gdf['stname'] == state)
                    filtered_gdf = gdf[conditions]
                
                elif request_data.get('state'):
                    state = request_data['state']
                    filtered_gdf = gdf[gdf['stname'] == state]
                
                else:
                    return JsonResponse({'error': 'No valid geographic criteria provided'}, status=400)
                    
                # Check if we found any matching features
                if filtered_gdf.empty:
                    return JsonResponse({'error': 'No matching geographic features found'}, status=404)
                    
                # Dissolve geometries if multiple features exist
                try:
                    if len(filtered_gdf) > 1:
                        filtered_gdf = filtered_gdf.dissolve()
                        # Ensure the dissolved geometry is valid
                        filtered_gdf.geometry = filtered_gdf.geometry.apply(fix_geometry)
                except Exception as e:
                    print(f"Error during dissolve operation: {str(e)}")
                    # If dissolve fails, try processing individual geometries
                    pass
                
                # Process each geometry
                for geometry in filtered_gdf.geometry:
                    if geometry is not None:
                        process_geometry(geometry)
                
                # Ensure we have some coordinates
                if not coordinates:
                    return JsonResponse({'error': 'Failed to extract valid coordinates'}, status=500)
                
                # For MultiPolygon, ensure proper nesting
                if len(coordinates) > 1:
                    coordinates = [coordinates]
                
                return JsonResponse({'coordinates': coordinates})
                
            except Exception as e:
                print(f"Error filtering or processing data: {str(e)}")
                return JsonResponse({'error': 'Error processing geographic data'}, status=500)
                
        except Exception as e:
            print(f"Error reading shapefile or processing request: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)