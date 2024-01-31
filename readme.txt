Welcome to my Github BizCardX: Extracting Business Card Data repository here I done a project in streamlit application.

The concept of this application is to fetch and filter the information from the image that was uploaded by the user and store in the database and perform the crud operation for the stored data.

Project Title: BizCardX: Extracting Business Card Data with OCR.

Skills Used: Python, Mysql, mysql-connector-python, streamlit, easyocr, git desktop.

Project Explaination:

1) Importing all the libraries that are required for the project.

2) connecting the project with mysql using mysql-connector.

3) 1st sidebar button called as Manual to show and explain and how to use the project for the user.

4) 2nd sidebar button called as Upload Image, here user should upload the image.

5) The uploaded image are scanned using easy ocr then filter the information that are shown in a dataframe.

6) When the user click the upload button then the dataframe information are uploaded to the database.

7) 3rd sidebar button used to edit the uploaded data, so user can create delete update the database using CRUD operation.

8) 4th siderbar button used to delete the row from the table by selecting the user name by selection dropdown bar.


Note:** there is no primary key is used beacuse it is not correct to find the unique for particular column.
