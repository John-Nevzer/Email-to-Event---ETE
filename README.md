Inroducing:

    Email to Event - ETE

    The Python App/Script automatically adds important events into the calendar.
    Created for you by: John Nevzer Avrung

    It uses AI running locally and a model you can choose. Supported two APIs:
    - First is default: Llama
    - Second: Full LM Studio API.

    Script has a tool for automatic addition to scheduler or cron (not fully tested).
    Script currently does not work with Microsoft Outlook and Google Gmail due to certification and API policy reasons.
    Fully tested on Seznam.cz* service provider. If you have a different provider with the same type of security or authentication, it should work.

    *Email uses standard IMAP.
    *Calendar uses iCalendar API and auth method.

    ------------------------------------------------------------------------

Setup:

All these steps are mandatory. If you do not follow them, serious consequences may occur for you. (You do not want to wake up and find out that all emails in your inbox are permanently deleted.)

    1. Download and unpack archive
    2. Install LM Studio - recommended for GPU compute
    3. Prepare your email box -> create new folder with normal name! -> go to the settings and create the new rule copying recieved email to the folder 
    4. Run run_settings.bat and set your authenticators for email*** and calendar, etc.
    5. Press the SAVE button
    6. Press the PLAN button to add task to Time scheduler
    7. Check by running run_ETE.bat


    **Model must understand your language, test before use!
    ***In email settings (usually on the web), create a new folder and set auto COPY! to receive emails in it, because they will be removed to avoid multiple processing of the same data/emails.

    ------------------------------------------------------------------------

Features:

        AI
        Automatization
        Local data processing
        User friendly
        (Multiplatform) in the future, currently on Windows prepared for Linux
        Task Scheduler
        Cron

    ------------------------------------------------------------------------

    Files structure in read_me_files.txt
    Function explanation in read_me_functions.txt
    Used library in Library requirements for venv.txt - it is a duplicate of requirements.txt

    Current version is in the name of the file Version X.X

    ------------------------------------------------------------------------
    ------------------------------------------------------------------------

Recommended components:
    Supported operating system: Windows 10/11
    Installed programs: LM studio, drivers for your hardware - especially for GPU/NPU card
    Accounts: email address, supported calendar - current support iCalendar/ with the same API.

    Minimum hardware specification:
    CPU: AMD Ryzen 5 3600 or Core i5-14600K
    RAM: 16GB - for small models/poor performance, 32GB - for good results (depends on language. Some models can only understand English or poorly support your language)
    Storage: LM studio with libraries approximately 5GB, LLM model from 5GB to "infinity" (good model approximately 10-20GB), ETE app 200MB. Approx total 20-25GB
    GPU: Any or none. For better performance, some with NPU/cores for neural processing (tensor cores - Nvidia, matrix cores - AMD)

    ------------------------------------------------------------------------

Work cycle of program:
    Currently, the app works only as a single shot. An on-demand work version is planned but not yet in development.

    1. App is called by task scheduler -> run a file run_ETE.bat
    2. App reads email in the folder in your email (multiple email address support is planned, but not supported yet)
    3. If no emails are found, the program ends itself and does not load the model (LLM).
    4. Else, it loads the model and proceeds with the emails.
    5. It writes the found events to the calendar.
    6. Logs out from email client via SMTP and calendar.
    7. Unloads the model and ends the task.
