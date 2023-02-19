from fastapi import FastAPI,Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import motor.motor_asyncio
from utilities import *
from models import *
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig

app = FastAPI()

origins = [
    "*",
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_DETAILS = "" # mongo uri

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.hackathon
Transcriptions = database.get_collection("Transcriptions")
Users = database.get_collection("Users")

#mail config
conf = ConnectionConfig(
    MAIL_USERNAME = "studypatt@gmail.com",
    MAIL_PASSWORD = "sxzhjylmlgmcbkyq",
    MAIL_FROM = "studypatt@gmail.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False
)



async def send_mail(subject,email,body):
    fm = FastMail(conf)
    message = MessageSchema(
        subject=subject,
        recipients=email,
        body=body,
        subtype="html"
    )
    await fm.send_message(message)

@app.get('/')
def index():
    return {'message':"Hello World"}


@app.post('/create')
async def create(transcript: TranscriptionModel ):
    try:
        print(transcript.video_url)
        # transcript = json.loads(transcript)
        print(transcript)
        video_url = transcript.video_url
        user_id = str(transcript.user_id)
        chapter_name = str(transcript.chapter_name)
        subject_name = str(transcript.subject_name)


        transcription,title = get_transcription(video_url)
        chunks = get_chunks(transcription['text'])
        print(type(transcription['text']))

        summarries = []

        for para in chunks:
            summary = get_summary(para)
            summarries.append(summary)    
        obj = {'title':str(title),'chunks':str(chunks),'summary': str(summarries), 'user_id': user_id, 'chapter_name': chapter_name, 'video_url': video_url }
        
        await Transcriptions.insert_one(obj)
        obj['_id'] = str(obj['_id']) 
        return obj

    except Exception as e:
        print("Error ", str(e))
        return {'message': 'Server Error : ' + str(e)}


@app.get("/gettranscripts/{user_id}")
async def get_transcripts(user_id: str):
    try:
        print(user_id)
        obj = Transcriptions.find({'user_id': user_id})
        obj = await obj.to_list(length=100)
        print(obj)
        for i in range(len(obj)):
            obj[i]['_id'] = str(obj[i]['_id'])
        return obj
    except Exception as e:
        return {'message': 'Server Error : ' + str(e)}

@app.post("/ocr_to_notes")
async def ocr_to_notes(data: OCRToNotesModel):
    try:
        print(data)
        user_id = str(data.user_id)
        chapter_name = str(data.chapter_name)
        subject_name = str(data.subject_name)
        text = str(data.text)

        chunks = get_chunks(text)
        summarries = []

        for para in chunks:
            summary = get_summary(para)
            summarries.append(summary)    
        obj = {'chunks':str(chunks),'summary': str(summarries), 'user_id': user_id, 'chapter_name': chapter_name }
        
        await Transcriptions.insert_one(obj)
        obj['_id'] = str(obj['_id']) 
        return obj

    except Exception as e:
        return {'message': 'Server Error : ' + str(e)}


@app.get('/recommend_videos')
async def get_recommended_videos(data: userDataModel):
    try:
        user_id = data.user_id
        obj = Transcriptions.find({'user_id': user_id},{"chunks":1})

        obj = await obj.to_list(length=100)
        
        merged = []
        for i in range(len(obj)):
            obj[i]['_id'] = str(obj[i]['_id'])
            temp = ""
            for chunk in obj[i]['chunks']:
                temp = temp + chunk
            merged.append(temp)

        recom = get_recommendations(merged)
        print(recom)
        return {"recommendations":recom}
    
    except Exception as e:
        return {'message': 'Server Error : ' + str(e)}



@app.post('/register')
async def registerUser(data : UserModel):
    try:
        print(data)
        obj = await Users.find_one({'email': data.email})
        if obj is None:
            obj = {
                'email': data.email,
                'password': data.password,
                'name': data.name,
                'mobile': data.mobile,
            }
            await Users.insert_one(obj)
            await send_mail("Sign Up Confirmation | StudyPat!", [data.email], "Greetings from StudyPat! \n\n Your Account has been successfully registered to StudyPat!")
            return {
                'email': data.email,
                'message': 'User Created Successfully'
            }, 200
        return {'message': 'User Alredy Exist'}
    except Exception as e:
        return {'message': 'Server Error : ' + str(e)}

@app.post('/login')
async def loginUser(data : LoginModel):
    try:
        obj = await Users.find_one({'email': data.email})
        print("User : ",str(obj['_id']))

        if obj is None:
            return {'message': 'User doesn\'t exist.'}
        if obj['password'] == data.password:
            return {
                'email': obj['email'],
                'user_id': str(obj['_id']),
                'user_name': obj['name'],
                'mobile': obj['mobile']
            }
        return {"message": 'Invalid credentials'}
    except Exception as e:
        return {'message': 'Server Error' + str(e)}
    

@app.get('/get_article')
async def get_article(article: LinkModel):
    try:
        url = article.link
        text = get_article_text(url)
        return {"article":text}
    
    except Exception as e:
        return {'message': 'Server Error : ' + str(e)}
