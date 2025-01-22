
RUNINNG
make `.env` in the same folder as this README.md, file with:

    OPENAI_API_KEY= "XXXXXXXXXXX"
    GROQ_API_KEY = "XXXXXXXXXXX"
    FB_USERNAME = "XXXXXXXXXXX"
    FB_PASSWORD = "XXXXXXXXXXX"
    KP_USERNAME = "XXXXXXXXXXX"
    KP_PASSWORD = "XXXXXXXXXXX"


Update database:

    cd lib
    python kp_scrape.py
    python fb_scrape.py

Run web app:

    python app.py


Add database geosrbija_parcele.sqlite to data folder

TODO:

Use https://huggingface.co/microsoft/Phi-3-vision-128k-instruct or some other mulitmodal to do OCR on date images

https://github.com/microsoft/Phi-3CookBook/blob/main/md/03.Inference/Vision_Inference.md
