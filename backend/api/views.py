from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.middleware.csrf import get_token
import json
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from PIL import Image
import numpy as np
import os
#from face_recognition_function import verify_faces
import cv2
from django.middleware.csrf import rotate_token
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
import verify_func
import tensorflow as tf
import keras.layers as Layer
import keras
from L1layer import L1Dist



@login_required
def check_auth(request):
    return JsonResponse({"authenticated":True})



@ensure_csrf_cookie
def csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})
    




def check_session(request):
    if request.session.get("registration_data"):
        return JsonResponse({"message": "Session exists"}, status=200)
    else:
        return JsonResponse({"error": "Session not found"}, status=404)


@csrf_protect
def login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")
        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON"}, status=400)

        if email and password:
            user = authenticate(request, username=email, password=password)
            #print(User)
            if user is not None:
                request.session["user_email"] = email
                auth_login(request,user)

                return JsonResponse({"message": "Login details verified, proceed with face recognition"}, status=200)
            else:
                return JsonResponse({"message": "Invalid login details"}, status=401)
        else:
            return JsonResponse({"message": "Email and password are required"}, status=400)
    else:
        return JsonResponse({"message": "Invalid request method"}, status=405)





def preprocess(image_array):
    img = tf.convert_to_tensor(image_array, dtype=tf.float32)
    img = tf.image.resize(img, (100, 100))
    img = img / 255.0  
    return img


def verify_func(model,input_img,validation_img,verification_threshold):
    #results=[]
    input_img = preprocess(input_img)
    validation_img = preprocess(validation_img)

    # Stack and expand dimensions
    images = np.array([input_img, validation_img])
    images = np.expand_dims(images, axis=0)  # Now shapes should be compatible for prediction

    result = model.predict(list(np.expand_dims([input_img,validation_img],axis=1)))

    verified = result[0] >= verification_threshold

    return verified




@csrf_protect
def verify(request):
    if request.method == 'POST':
        user_email = request.session.get("user_email")
        if not user_email:
            return JsonResponse({"message": "User email not found in session"}, status=400)

        user_image = request.FILES.get('profile_image')
        if not user_image:
            
            return JsonResponse({"message": "No image uploaded"}, status=400)
        

        user_detail = UserProfile.objects.filter(user__email=user_email).first()
        if not user_detail:
            return JsonResponse({"message": "User not found"}, status=404)

        try:
            old_picture = user_detail.profile_image.path
            old_picture=cv2.imread(old_picture)
            old_picture = np.array(old_picture)

            #img= cv2.cvtColor(old_picture,cv2.COLOR_BGR2RGB)

            uploaded_image = Image.open(user_image)
            image_array = np.array(uploaded_image)
            #image_rgb = cv2.cvtColor(image_array,cv2.COLOR_BGR2RGB)
            

            model_path = r'C:\Users\THINKPAD T460s\Documents\Web base facial authentication\backend\siamese_model.h5'
            model=tf.keras.models.load_model(model_path, custom_objects={'L1Dist':L1Dist})
            #is_match= verify_faces(img,image_rgb)
            is_match=verify_func(model,old_picture,image_array,0.8)
            print(is_match)
            if is_match:
                # print(request.session["verified"],"e dey")
                return JsonResponse({"message": "Verification successful"}, status=200)
            else:
                answer= JsonResponse({"error": "Face does not match, access denied"}, status=403)
                auth_logout(request)
                request.session.flush()
                return answer
            
        except IndexError:
            return JsonResponse({"error": "No face detected in the uploaded image"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
            


# def main_page(request):
#     if request.method == 'POST':
#         confirm_verification= request.session.get("verified")
#         print(confirm_verification, "e exist")
#         if not confirm_verification:
#             return JsonResponse({"message": "Not verified"}, status=400)
#         return JsonResponse({"message":"Successful"},status=200)













def logout(request):
    auth_logout(request)
    rotate_token(request) 
    request.session.flush()  # Refresh the CSRF token
    response = JsonResponse({"message": "Logout successful"}, status=200)
    return response





@csrf_protect
def register(request):
    if(request.method=="POST"):
        Data= json.loads(request.body)
        EMAIL = Data.get("email")
        PASSWORD = Data.get("password")
        PASSWORD_CONFIRMATION  = Data.get("password2")

        if (PASSWORD == PASSWORD_CONFIRMATION ):
            user = User.objects.filter(email=EMAIL).first()
            if user:
                return JsonResponse({"error": "User already exists"}, status=400)
            else:
                request.session['registration_data'] = {
                            'email': EMAIL,
                            'password': PASSWORD}
            
                return JsonResponse({"message":"session data saved"},status=200)
        else:
            return JsonResponse({"error":"password does not match"},status=400)
        


@csrf_protect
def upload_image(request):
    if request.method == 'POST':
        user_image = request.FILES.get('profile_image')
        
        if not user_image:
            return JsonResponse({"error": "No Image uploaded"}, status=400)

        User_data = request.session.get("registration_data")
        if not User_data:
            return JsonResponse({"error": "Registration data not found in session"}, status=400)

        Email = User_data.get("email")
        PassWord = User_data.get("password")

        if not Email or not PassWord:
            return JsonResponse({"error": "Email or password missing in registration data"}, status=400)
        
        if User.objects.filter(email=Email).exists():
            return JsonResponse({"message": "User with this email already exists"}, status=400)
        new_user = User.objects.create_user(username=Email, email=Email, password=PassWord)
        new_user_profile = UserProfile(user=new_user, profile_image=user_image)
        new_user_profile.save()

        auth_login(request, new_user)

        if 'registration_data' in request.session:
            del request.session['registration_data']

        return JsonResponse({"Message": "Registration Successful"}, status=200)


























# def Login(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             email = data.get("email")
#             password = data.get("password")
        
#         except json.JSONDecodeError:
#             return JsonResponse({"message": "Invalid JSON"}, status=400)

#         if email and password:
#             user = authenticate(request, username=email, password=password)
#             if user is not None:
#                 request.session["user_email"] = email
#                 auth_login(request, user)

#                 return JsonResponse({"message": "Login successful"}, status=200)
#             else:
#                 return JsonResponse({"message": "Invalid login details"}, status=401)
#         else:
#             return JsonResponse({"message": "Email and password are required"}, status=400)
#     else:
#         return JsonResponse({"message": "Invalid request method"}, status=405)
    


# stored_image = face_recognition.load_image_file(old_picture)
            # img = cv2.resize(stored_image,(0,0),None,0.25,0.25)
            # stored_image_encoding = face_recognition.face_encodings(img)[0]

            # img_new = cv2.resize(uploaded_image,(0,0),None,0.25,0.25)
# def verify(request):
#     if request.method == 'POST':
#         user_email = request.session.get("user_email")
#         if not user_email:
#             return JsonResponse({"message": "User email not found in session"}, status=400)

#         user_image = request.FILES.get('profile_image')
#         if not user_image:
#             return JsonResponse({"message": "No image uploaded"}, status=400)

#         user_detail = UserProfile.objects.filter(user__email=user_email).first()
#         if not user_detail:
#             return JsonResponse({"message": "User not found"}, status=404)

#         try:
#             oldPicture= user_detail.profile_image.path
#             image = face_recognition.load_image_file(oldPicture)
#             OldImage_encoding = face_recognition.face_encodings(image)[0]
#             comparism = faceCompare(user_image,OldImage_encoding)
#             if comparism[0]:  # Access the first value of the list
#                 auth_login(request, user_detail.user)
#                 return JsonResponse({"message": "Verification successful"}, status=200)
#             else:
#                 return JsonResponse({"message": "You are not the owner of this account"}, status=403)
        
#         except IndexError:
#             return JsonResponse({"message": "No face detected in the uploaded image"}, status=400)



# def upload_image(request):
#     if request.method == 'POST':
#         user_image = request.FILES.get('profile_image')
#         # print("good")
#         if not user_image:
#             return JsonResponse({"error": "No Image uploaded"}, status=400)

#         User_data = request.session.get("registration_data")
#         if not User_data:
#             return JsonResponse({"error": "Registration data not found in session"}, status=400)

#         Email = User_data.get("email")
#         PassWord = User_data.get("password")

#         if not Email or not PassWord:
#             return JsonResponse({"error": "Email or password missing in registration data"}, status=400)
        
#         userFetch = UserProfile.objects.filter(user__email=Email).first()
#         if userFetch is not None:
#             return JsonResponse({"message":"User already exist"}, status=400)
#         else:
#             # Create new user
#             new_user = User.objects.create_user(username=Email, email=Email, password=PassWord)
#             ImageEncoding = faceEncoding(userFetch.profile_image.path)

#             new_user_profile = UserProfile(user=new_user, profile_image=user_image, face_encoding=ImageEncoding)
#             new_user_profile.save()


#         # Log the user in after registration
#         auth_login(request, new_user)

#         # Clean up session data
#         if 'registration_data' in request.session:
#             del request.session['registration_data']

#         return JsonResponse({"Message": "Registration Successful"}, status=200)

       