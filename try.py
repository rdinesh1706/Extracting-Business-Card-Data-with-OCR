import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
import mysql.connector
from PIL import Image
import cv2
import os
import matplotlib.pyplot as plt
import re

# easy OCR detection
reader = easyocr.Reader(['en'])

# Connecting mysql database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rdx@17",
    database="biz_card"
)

mycursor = mydb.cursor(buffered=True)
query = '''CREATE TABLE IF NOT EXISTS card_dataaa
                (Card_Holder_Name TEXT,
                    Designation TEXT,
                    Company_Name TEXT,
                    Phone_Number VARCHAR(50),
                    Email TEXT,
                    Website TEXT,
                    Area VARCHAR(50), 
                    City TEXT,
                    State TEXT,
                    Pincode VARCHAR(10),
                    Image LONGBLOB
                    )'''
mycursor.execute(query)
mydb.commit()

# streamlit page background setup

st.set_page_config(page_title="Business Card Data Extraction with OCR",
                   layout="wide",
                   initial_sidebar_state="expanded",)
st.markdown("<h1 style='text-align: center; color: white;'>Business Card Data Extraction</h1>",
            unsafe_allow_html=True)
st.divider()

# This function explain and how to use the project for the user


def manual():
    st.subheader("About the Application")
    st.write(" Users can insert the business card by using easyOCR we are storing the fetched information of the card in the mysql and we can edit or delete the information according to the users requirement ")
    st.subheader("What is Easy OCR?")
    st.write("EasyOCR is a font-dependent printed character reader based on a template matching algorithm. It has been designed to read any kind of short text part numbers, serial numbers, expiry dates, manufacturing dates, lot codes, printed on labels or directly on parts")
    st.subheader("Existing Data in Database")
    mycursor.execute(''' select Card_Holder_Name as Card_Holder_Name,Designation as Designation, Company_Name as Company_Name,Phone_Number as Phone_Number,Email as Email,Website as Website,Area as Area,City as City,State as State, Pincode as Pincode from card_dataaa''')

    updated_df = pd.DataFrame(mycursor.fetchall(),
                              columns=["Card_Holder_Name", "Designation", "Company_Name",
                                       "Phone_Number", "Email", "Website", "Area", "City", "State", "Pin_Code"])
    st.write(updated_df)


def Upload_Image():
    st.subheader("Business Card")
    # Getting the image from the user by using file uploader
    image_files = st.file_uploader(
        "Upload the Business Card below:", type=["png", "jpg", "jpeg"])

    def save_card(image_files):
        uploaded_cards_dir = os.path.join(os.getcwd(), "bizcard")
        with open(os.path.join(uploaded_cards_dir, image_files.name), "wb") as f:
            f.write(image_files.getbuffer())

    if image_files != None:
        col1, col2 = st.columns(2, gap="large")
        with col1:
            img = image_files.read()
            st.markdown(" Business Card has been uploaded")
            st.image(
                img, caption='The image has been uploaded successfully', width=500)
            save_card(image_files)

        with col2:
            saved_img = os.getcwd() + "\\" + "bizcard" + "\\" + image_files.name
            image = cv2.imread(saved_img)
            res = reader.readtext(saved_img)
            st.markdown("Data has been extracted from images")

            def image_preview(image, res):
                for (bbox, text, prob) in res:
                    # unpack the bounding box
                    (tl, tr, br, bl) = bbox
                    tl = (int(tl[0]), int(tl[1]))
                    tr = (int(tr[0]), int(tr[1]))
                    br = (int(br[0]), int(br[1]))
                    bl = (int(bl[0]), int(bl[1]))
                    cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                    cv2.putText(image, text, (tl[0], tl[1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                plt.rcParams['figure.figsize'] = (15, 15)
                plt.axis('off')
                plt.imshow(image)
            b = image_preview(image, res)
            st.set_option('deprecation.showPyplotGlobalUse', False)
            st.pyplot(b)

        # using easy OCR we are getting the data from the image
        saved_img = os.getcwd() + "\\" + "bizcard" + "\\" + image_files.name
        result = reader.readtext(saved_img, detail=0, paragraph=False)

        # Converting image to binary to upload to sql database
        def img_to_binary(file):
            # Convert image data to binary format
            with open(file, 'rb') as file:
                binaryData = file.read()
            return binaryData
        # all the extraced key values are stored in these list present inside the dictionary
        data = {"Card_Holder_Name": [],
                "Designation": [],
                "Company_Name": [],
                "Phone_Number": [],
                "Email": [],
                "Website": [],
                "Area": [],
                "City": [],
                "State": [],
                "Pincode": [],
                "image": img_to_binary(saved_img)
                }

        # this function helps filter and to save the key details to store in particular list
        def get_data(res):
            for ind, i in enumerate(res):

                # To get website url
                if "www " in i.lower() or "www." in i.lower():
                    data["Website"].append(i)
                elif "WWW" in i:
                    data["Website"] = res[4] + "." + res[5]

                # To get email id
                elif "@" in i:
                    data["Email"].append(i)

                # To get phone number
                elif "-" in i:
                    data["Phone_Number"].append(i)
                    if len(data["Phone_Number"]) == 2:
                        data["Phone_Number"] = " & ".join(data["Phone_Number"])
                # To get company name
                elif ind == len(res) - 1:
                    data["Company_Name"].append(i)

                # To get card holder name
                elif ind == 0:
                    data["Card_Holder_Name"].append(i)

                # To get designation
                elif ind == 1:
                    data["Designation"].append(i)

                # To get area
                if re.findall('^[0-9].+, [a-zA-Z]+', i):
                    data["Area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+', i):
                    data["Area"].append(i)

                # To get city name
                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*', i)
                if match1:
                    data["City"].append(match1[0])
                elif match2:
                    data["City"].append(match2[0])
                elif match3:
                    data["City"].append(match3[0])

                # To get state name
                state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
                if state_match:
                    data["State"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
                    data["State"].append(i.split()[-1])
                if len(data["State"]) == 2:
                    data["State"].pop(0)

                # To get pincode of the city
                if len(i) >= 6 and i.isdigit():
                    data["Pincode"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]', i):
                    data["Pincode"].append(i[10:])
        # to save and present all the data in dataframe
        get_data(result)
        df = pd.DataFrame(data)
        st.success("### Data Extracted!")
        st.write(df)

        # if we press the button all the data present in dataframe are uploaded to database(sql)
        if st.button("Upload to Database"):
            for i, row in df.iterrows():
                query1 = '''insert into card_dataaa(Card_Holder_Name,Designation,Company_Name,Phone_Number,Email,Website,Area,City,State,Pincode,Image)
                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                mycursor.execute(query1, tuple(row))
                mydb.commit()
                mycursor.execute(
                    '''Select Card_Holder_Name,Designation,Company_Name,Phone_Number,Email,Website,Area,City,State,Pincode from card_dataaa''')
                updated_df = pd.DataFrame(mycursor.fetchall(),
                                          columns=["Card Holder Name", "Designation", "Company Name",
                                                   "Phone Number", "Email", "Website", "Area", "City", "State", "Pin_Code"])
                st.success("Uploaded to database successfully!")
                st.write(updated_df)


def Make_Changes():
    st.markdown("Change the data here")

    try:
        mycursor.execute("select Card_Holder_Name from card_dataaa")
        result = mycursor.fetchall()
        business_cards = {}
        for row in result:
            business_cards[row[0]] = row[0]
        options = ["select card"] + list(business_cards.keys())

        # by using the select box we can edit the table data and enter the values

        selected_card = st.selectbox("**select a card", options)
        if selected_card == "select card":
            st.write("Card not selected")
        else:
            st.markdown("Update or modify the data below")
            mycursor.execute(
                ''' select Card_Holder_Name,Designation,Company_Name, Phone_Number,Email,Website,Area,City,State,Pincode from card_dataaa where Card_Holder_Name=%s''', (selected_card,))
            result = mycursor.fetchone()

            # DISPLAYING ALL THE INFORMATIONS
            Card_Holder = st.text_input("Card_Holder", result[0])
            Designation = st.text_input("Designation", result[1])
            Company_Name = st.text_input("Company_Name", result[2])
            Mobile_Number = st.text_input("Mobile Number", result[3])
            Email = st.text_input("Email", result[4])
            Website = st.text_input("Website", result[5])
            Area = st.text_input("Area", result[6])
            City = st.text_input("City", result[7])
            State = st.text_input("State", result[8])
            Pin_Code = st.text_input("Pincode", result[9])

            # if we press the button
            if st.button("Change the Data in DB"):

                mycursor.execute(''' update card_dataaa  set Card_Holder_Name = %s, Designation = %s, Company_Name = %s, Phone_Number = %s, Email = %s, Website = %s, Area = %s, City = %s, State = %s, Pincode = %s where Card_Holder_Name = %s''',
                                 (Card_Holder, Designation, Company_Name, Mobile_Number, Email, Website, Area, City, State, Pin_Code, selected_card))

                mydb.commit()
                st.success("Changes updated Successfully")

        # show all the data in a dataframe format
        if st.button("View_Data"):
            mycursor.execute(
                ''' Select Card_Holder_Name, Designation, Company_Name, Phone_Number, Email, Website, Area, City, State, Pincode from card_dataaa ''')
            updated_df_v2 = pd.DataFrame(mycursor.fetchall(), columns=[
                "Card_Holder_Name", "Designation", "Company_Name", "Phone_Number", "Email", "Website", "Area", "City", "State", "Pincode"])
            st.write(updated_df_v2)

    except:
        st.warning("There is no data like that")


def Deletion():
    st.subheader("Delete the entire data")
    try:
        mycursor.execute("select Card_Holder_Name from card_dataaa")
        result = mycursor.fetchall()
        business_cards = {}
        for row in result:
            business_cards[row[0]] = row[0]
        options = ["None"] + list(business_cards.keys())
        selected_card = st.selectbox("** Select a card", options)
        if selected_card == "None":
            st.write("no data selected")
        else:
            st.write(
                f" you selected this :red[**{selected_card}**] card to delete ")
            st.write("Confirm to delete this data?")
            if st.button("Confirm delete"):
                mycursor.execute(
                    f"Delete from card_dataaa where Card_Holder_Name = '{selected_card}'")
                mydb.commit()
                st.success("Deleted from database")

        if st.button("View data"):
            mycursor.execute(
                ''' select Card_Holder_Name, Designation, Company_Name, Phone_Number, Email, Website, Area, City, State, Pincode from card_dataaa ''')
            updated_df_v3 = pd.DataFrame(mycursor.fetchall(), columns=[
                "Card_Holder_Name", "Designation", "Company_Name", "Phone_Number", "Email", "Website", "Area", "City", "State", "Pincode"])
            st.write(updated_df_v3)

    except:
        st.warning("No data is in database")


with st.sidebar:
    st.title("Biz_Card")
    st.title("Press the button")
    show_table = st.radio(
        "Press the button for the view 👇",
        ["Manual", "Upload Image", "Make Changes", "Deletion"],
    )


if show_table == "Manual":
    manual()
elif show_table == "Upload Image":
    Upload_Image()
elif show_table == "Make Changes":
    Make_Changes()
elif show_table == "Deletion":
    Deletion()
