import environ,io
import datetime
from django.http.response import JsonResponse
from io import StringIO
from MongoDB.msvisionControl import consumeVision
from MongoDB.signedURL import generate_signed_url
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from MongoDB.serializers import ExtractSerializer, UserSerializer, ModelSerializer, FieldSerializer
from MongoDB.models import User, Document, Field, File, ExtractFIle
from MongoDB.msbucketControl import  msupload, upload_Excel, download_byt

import pdf2image
from django.conf import settings
import uuid
import re
import pandas as pd
from collections import defaultdict

env = environ.Env()

environ.Env.read_env()

keyAPI = env('API_KEYS')
bucket = env('BUCKET')

def processData(input):   
    
    t={}           
    print(input)
    def get_values_ms():
        i = 0 
        for x in input.read_results:
            for line in x.lines:
                for word in line.words:
                    # for character in word.characters:
                    ver = word.bounding_box
                    x1,y1,x2,y2=ver[0],ver[1],ver[2],ver[3]
                    t[i] = [x1,y1,x2-x1,y2-y1,word.text]
                    i = i + 1
    get_values_ms()
    df = {'x':[],'y':[],'w':[],'h':[],'values':[]}
    for x in t.values():
        df['x'].append(x[0])
        df['y'].append(x[1])
        df['w'].append(x[2])
        df['h'].append(x[3])
        df['values'].append(x[4])
    return df


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def savemodel(request):
    coordinates = request.data['coordinate']
    modelname = request.data['modelname']
    modelid = request.data['modelID']
    print(modelid,type(modelid))
    success = 0
    for y1 in coordinates.values():
        y = y1
        for label, coor in y.items():
            tol = [17.02, 22.016, 18.95, 17.37]
            li1 = re.findall(r'\d+\.*\d*', str(coor))
            d = 0
            li2 = []
            page = []
            while(d < len(li1)):
                page.append(li1[d])
                li2.append(li1[d+1:d+5])
                d += 5
            li = []
            for x in li2:
                print(x)
                x[2], x[3] = x[3], x[2]
                x = list(map(float, x))
                li.append(x)
            li2 = []
            for x in li:
                li2 = [u*v for u, v in zip(x, tol)]
            try:
                snippet = Field.objects.filter(modelname=model)
            except Field.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            field1 = Field.objects.filter(modelname=modelname, fieldname=label).update(fieldcoor=[page, li2])         
            # snippet.save()
            print('test', (field))
            success += 1
    try:
        snippet = Document.objects.filter(modelname=(modelname))
    except Document.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    snippet.update(finished= True)
    
    return JsonResponse(data="Success " + str(success), safe=False)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def text(request):
    coordinates = request.data['coordinate']

    file = File.objects.get(modelname=request.data['modelname'])
    detail = re.sub("'", '"', file.filedetail)
    detail = re.sub('''"""''', '"', detail)
    detail = detail.replace('""', ''''"''')
    df1_list = {}
    
    print(eval(detail))
    for n, x in eval(detail).items():
        df = x
        df1 = pd.DataFrame(df)
        df1_list[str(n+1)] = df1
    print('check',df1_list)
    text = {}

    for n, x1 in coordinates.items():
        uniq_y = []
        for x in (df1_list[n][['y', 'h']].values):
            #     print(x,uniq_y)
            if set(x) not in uniq_y:
                uniq_y.append(','.join(list(map(str, x))))
        uniq_y1 = list(set(uniq_y))
        uniq_y1 = [list(map(float, x.split(','))) for x in uniq_y1]
        for label, coor in x1.items():
            # print(coordinates)
            tol = [17.02, 22.016, 18.95, 17.37]
            li1 = re.findall(r'\d+\.*\d*', str(coor))
            d = 0
            li2 = []
            while(d < len(li1)):
                li2.append(li1[d:d+4])
                d += 4
            li = []
            for x in li2:
                x[2], x[3] = x[3], x[2]
                x = list(map(float, x))
                li.append(x)
            li2 = []
            for x in li:
                li2.append([u*v for u, v in zip(x, tol)])
            uniq_y1.sort()
            df1 = df1_list[n].sort_values(['y', 'x'])
            x_val = {}
            # text = {}
            for y_ in enumerate(li2):
                text[label] = []
                y = y_[1]
                for i__ in uniq_y1:
                    i_ = list(i__)
                    # print(i_, y)
                    if (i_[0] <= y[1]+y[3] and i_[0] >= y[1]):
                        if y[1] not in x_val.keys():
                            x_val[y[1]] = []
                        for k in df1[(df1['y'] == i_[0]) & (df1['h'] == i_[1])].iterrows():
                            i = k[1]
                            if (i['x'] >= y[0]-10):
                                if (y[2]+y[0] < i['x']):
                                    break
                                x_val[y[1]].append(i['x'])
                                if (x_val[y[1]][-1]-x_val[y[1]][0]+i['w'] > y[2]):
                                    break
                                i_ = i['values'].replace('''"""''', '''"'"''')
                                print(i_)
                                text[label].append(
                                    str({"page": n, "text": i_, "postiton":k[1]['x']}))
            # print(n, text[label])
    print(text)
    return JsonResponse(data=text, safe=False)


@ api_view(['POST'])
@ permission_classes((permissions.AllowAny,))
def extractValesAll(request):
    # files = request.data['files']
    model = request.data['modelname']
    filelist = request.data['filelist']
    print(request.data)
    user = request.data['user']

    try:
        snippet = Field.objects.filter(modelname=model)
    except Field.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        user_details = User.objects.get(username=user)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    user_ = UserSerializer(user_details).data

    email = user_['email']
    t_ = (FieldSerializer(snippet, many=True).data)
    li2 = {}
    page = {}
    for x in t_:
        print(x)
        li1 = eval(x['fieldcoor'])
        page[x['fieldname']] = li1[0][0]
        li2[x['fieldname']] = li1[1]

    text1 = defaultdict(list)
    for file in filelist:
        try:
            snippet = ExtractFIle.objects.filter(
                modelname=model, filename=file)
        except ExtractFIle.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        a = (ExtractSerializer(snippet, many=True))
        for x__ in a.data:
            print(x__)
            x_ = eval(x__['eachfile'])
            filename = x__['originalname']
            text1['File name'].append(
                str(filename))
            for n, x2 in enumerate(x_):
                img= generate_signed_url(settings.UPLOAD_ROOT+'/'+x2)
                boxes = consumeVision(img)
                i = 0
                df1 = processData(boxes)
                df1 = pd.DataFrame(df1)
                uniq_y = []
                for x in (df1[['y', 'h']].values):
                    #     print(x,uniq_y)
                    if set(x) not in uniq_y:
                        uniq_y.append(','.join(list(map(str, x))))
                uniq_y1 = list(set(uniq_y))
                uniq_y1 = [list(map(float, x.split(','))) for x in uniq_y1]

                for label, coor in li2.items():
                    if int(page[label]) != n+1:
                        continue
                    v2, v3 = '', ''
                    v2 = str(label)
                    li = []
                    x = coor
                    x = list(map(float, x))
                    li.append(x)
                    uniq_y1.sort()
                    df1 = df1.sort_values(['y', 'x'])
                    x_val = {}
                    # text = {}
                    for y_ in enumerate(li):
                        # text[''].append(label)
                        y = y_[1]
                        for i__ in uniq_y1:
                            i_ = list(i__)
                            # print(i_, y)
                            if (i_[0] <= y[1]+y[3] and i_[0] >= y[1]):
                                if y[1] not in x_val.keys():
                                    x_val[y[1]] = []
                                for k in df1[(df1['y'] == i_[0]) & (df1['h'] == i_[1])].iterrows():
                                    i = k[1]
                                    if (i['x'] >= y[0]-10):
                                        if (y[2]+y[0] < i['x']):
                                            break
                                        x_val[y[1]].append(i['x'])
                                        if (x_val[y[1]][-1]-x_val[y[1]][0]+i['w'] > y[2]):
                                            break
                                        i_ = i['values'].replace(
                                            '''"""''', '''"'"''')
                                        v3 += ' '+i_
                    text1[str(v2)].append(str(v3))
    textStream = StringIO()
    print(text1)
    filename_xl = str(uuid.uuid4())+'.csv'
    pd.DataFrame(text1).to_csv(textStream)
    
    upload_Excel(filename_xl,textStream.getvalue())
    tempUrl = generate_signed_url('Outputs_excel/'+str(datetime.datetime.now()).split()[0]+'/'+ filename_xl)
    return Response(data=tempUrl)


@ api_view(['POST'])
@ permission_classes((permissions.AllowAny,))
def uploadfiles(request):
    file = request.FILES['file']
    originalname = request.data['filename']
    # print(file['name'])
    extract = ExtractFIle(
        filename=str(uuid.uuid4())+str(request.FILES['file'].name)[-4:],
        # file=file,
        modelname=request.data['modelname'],
        originalname=originalname
    )
    # extract.save()
    file_list = []  
    msupload(settings.UPLOAD_ROOT+'/'+str(extract.filename)[
        :-4]+'_folder'+'/'+extract.filename, file)
    byte = download_byt(settings.UPLOAD_ROOT+'/'+str(
        extract.filename)[:-4]+'_folder'+'/'+extract.filename)
    img = pdf2image.convert_from_bytes(byte)
    for n, i in enumerate(img):
        # print(filename_img)
        img_byte_arr = io.BytesIO()
        i.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()        
        msupload(settings.UPLOAD_ROOT+'/'+str(extract.filename)[
            :-4]+'_folder'+'/'+extract.filename[:-4]+'_'+str(n)+'.jpg', img_byte_arr)
        file_list.append(str(extract.filename)[
                         :-4]+'_folder'+'/'+extract.filename[:-4]+'_'+str(n)+'.jpg')
    extract.eachfile = file_list
    # print(extract.filename)
    extract.save()
    return JsonResponse(data=(extract.filename), safe=False)


@ api_view(['POST'])
@ permission_classes((permissions.AllowAny,))
def upload(request):
    print(request)
    file = File(
        filename=str(uuid.uuid4())+str(request.FILES['file'].name)[-4:],
        modelname=request.data['modelname']
    )
    # file.save()
    # print(file.filename)
    file_list = []
    file_list1 = []
    
    img = pdf2image.convert_from_bytes(request.FILES['file'].read())
    for n, i in enumerate(img):
        img_byte_arr = io.BytesIO()
        i.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()        
        msupload(settings.MEDIA_ROOT+'/'+str(file.filename)[
            :-4]+'_folder'+'/'+file.filename[:-4]+'_'+str(n)+'.jpg', img_byte_arr)
        file_list.append(str(file.filename)[
                         :-4]+'_folder'+'/'+file.filename[:-4]+'_'+str(n)+'.jpg')

        file_list1.append(generate_signed_url(settings.MEDIA_ROOT+'/'+str(file.filename)[
            :-4]+'_folder'+'/'+file.filename[:-4]+'_'+str(n)+'.jpg'))
    file.eachfile = file_list
    df_list = {}

    for n, x in enumerate(file_list):
        img= generate_signed_url(settings.MEDIA_ROOT+'/'+x)
        boxes = consumeVision(img)
        i = 0
        df = processData(boxes)
        df_list[n] = df
    file.filedetail = str(df_list)
    file.save()
    return JsonResponse(data=file_list1, safe=False)

@ api_view(['GET', 'PUT', 'DELETE'])
@ permission_classes((permissions.AllowAny,))
def user_detail(request, username, password):
    """
    Retrieve, update or delete a code snippet.
    """
    
    try:
        snippet = User.objects.get(username=username, password=password)
        
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(snippet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@ api_view(['GET', 'POST', 'PUT'])
@ permission_classes((permissions.AllowAny,))
def user(request):
    if request.method == 'POST':
        try:
            usernames = User.objects.filter(username=request.data['username']).exists()
            if usernames:
                return Response("Username already exist")
        except:
            pass
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response('success')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'PUT':
        snippet = User.objects.get(username = request.data['username'])
    usernames = User.objects.all()
    tutorials_serializer = UserSerializer(usernames, many=True)
    data = {}
    for x in tutorials_serializer.data:
        del x['password']
    print(tutorials_serializer.data)
    return JsonResponse(tutorials_serializer.data, safe=False)


@ api_view(['GET', 'PUT', 'DELETE'])
@ permission_classes((permissions.AllowAny,))
def model_detail(request, modelname):
    """
    Retrieve, update or delete a code snippet.
    """
    try:
        snippet = Document.objects.get(modelname=modelname)
    except Document.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ModelSerializer(snippet)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ModelSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@ api_view(['GET', 'POST'])
@ permission_classes((permissions.AllowAny,))
def model_field(request):
    print(request.data)
    ret = model1(request.data['modeldetails'])
    for x in request.data['fielddetails']:
        print(x)
        field(x)
    print(ret)
    return Response(ret)


def model1(request):
    serializer = ModelSerializer(data=request)
    if serializer.is_valid():
        serializer.save()
        return (serializer.data['id'])


@ api_view(['GET', 'POST','DELETE'])
@ permission_classes((permissions.AllowAny,))
def model(request):
    if request.method == 'POST':
        serializer = ModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return (serializer.data['id'])
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        serializer = Document.objects.filter(modelname=request.data['modelname'])
        serializer.delete()
        return Response('success')
    docs = Document.objects.all()
    model_serializer = ModelSerializer(docs, many=True)
    data = [x for x in model_serializer.data]
    return JsonResponse((data), safe=False)


@ api_view(['GET', 'POST', 'DELETE'])
@ permission_classes((permissions.AllowAny,))
def field_detail(request, modelname):
    """
    Retrieve, update or delete a code snippet.
    """

    if request.method == 'GET':
        snippet = Field.objects.filter(modelname=modelname)
        serializer = FieldSerializer(snippet, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'DELETE':
        try:
            sni = File.objects.filter(modelname=modelname).delete()
        except:
            pass
        snippet = Field.objects.filter(modelname=modelname)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    try:
        snippet = Field.objects.get(modelname=modelname)
    except Field.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = FieldSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def field(request):
    
    print(request)
    serializer = FieldSerializer(data=request)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
