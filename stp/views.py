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
from .service import weight_redisturb,normalize_data,rank_process 
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
        # find the rank 
        
        




# def calculate_ranks(list_of_dicts, normalized_weights):
#     # Initialize list to store scores
#     scores = []
    
#     # For each dictionary in the list
#     for data_dict in list_of_dicts:
#         total_score = 0
        
#         # For each normalized weight dictionary
#         for weight_dict in normalized_weights:
#             # Get the key and weight value from weight dictionary
#             weight_key = list(weight_dict.keys())[0]
#             weight_value = list(weight_dict.values())[0]
            
#             # Multiply data value with corresponding weight
#             if weight_key in data_dict:
#                 total_score += data_dict[weight_key] * weight_value
        
#         # Store the original data and its score
#         scores.append({
#             'data': data_dict['Districts'],
#             'score': total_score
#         })
    
#     # Sort scores in descending order
#     sorted_scores = sorted(scores, key=lambda x: x['score'], reverse=True)
    
#     # Add ranks
#     for i, score in enumerate(sorted_scores, 1):
#         score['rank'] = i
    
#     return sorted_scores
# # Create your views here.

# class GetRankData(APIView):
#     def post(self,request):
#         ls=request.data
#         ## this is getting heading
#         headings=[] 
#         headings.append(ls[0].keys())
#         ## logic is
#         headings=list(headings[0])
#         replaced_map={'Districts':'Index_val'}
#         updated_headings = [replaced_map.get(field, field) for field in headings]

#         for i in ls:
#             del i['id']

#         weight=Weight.objects.values(*updated_headings)
#         for i in weight:
#             del i['id']
#             del [i['Index_val']]
#         updated_heading=updated_headings[2:]
#         weights=list(weight)
#         weights=weights[0]
#         new_weight= weight_redisturb(weights,updated_heading)
#         print("new weightis ",new_weight)
#         ls,lst=normalize_columns(ls)
#         print(ls)
#         ans=calculate_ranks(ls,new_weight)
#         print("ans is ",ans)
#         return Response(ans,status=200)
