import streamlit as st
import serial
from serial import Serial
from time import sleep
import pandas as pd
from datetime import date
from datetime import datetime
from PIL import Image
import os



#Page-Setup-----------------------------------------------------------------------------------------------------------
st.set_page_config(
    page_title='AWS Torque Tester',
    page_icon=':eyes:',
    layout='wide',
    initial_sidebar_state='auto'
)


#---------------------------------------------------------------------------------------------------------------------
toasty = Image.open(r'C:\Users\luis.peguero\Desktop\Projects\AWS_DEF\toasty.png')
ztbanner = Image.open(r'C:\Users\luis.peguero\Desktop\Projects\AWS_DEF\ztbanner.png')
aws_f = r'C:\Users\luis.peguero\Desktop\Projects\AWS_DEF\torque_record'
main_column, s_column, t_column = st.beta_columns(3)
# nm_ = st.beta_container()
re_write = st.empty()
fail_image = st.empty()
asset_data = st.empty()
d_manipulate = st.empty()
in_side = st.empty()





#date/time
today = date.today()
today_time = datetime.now()
c_date = today.strftime('%m/%d/%y')
full_date = today_time.strftime('%m/%d/%y, %H:%M:%S')

#Dataframe-----------------------------------------------------------------------------------------------------------
csv_file = r'C:\Users\luis.peguero\Desktop\Projects\AWS_DEF\aws_torque_data.csv'
data = pd.read_csv(csv_file)
global df
df = pd.DataFrame(data)

#function to read AWS------------------------------------------------------------------------------------------------
hold1 = []
hold2 = []
result = None
@st.cache(suppress_st_warning=True)
def run():
    ser = serial.Serial(port='COM6',
                        baudrate=9600,
                        timeout=2 
    )
    buff = ''
    counterp = 0
    counterf = 0
    nm_value = float(df.loc[df['asset_tag'] == user_input, 'nominal'].iloc[0])
    minus = nm_value - (nm_value * 0.05)
    plus = nm_value + (nm_value * 0.05)
    while 1:
        buff = ser.readline().decode('ascii')
        str1 = buff
        a = str1.replace("Nm", "")
        try:
            b = float(a)
            if minus < b < plus:
                global result
                result = str1
                hold1.append(str1)
                counterp += 1
                with open(os.path.join(aws_f, f'{user_input}.txt'), 'a') as file:
                    file.writelines([full_date, ' | ','pass' ,' | ', user_input, ' | ', torque_id, ' | ', str1 ])
                re_write.success(str1 + 'Pass')
                sleep(1.5)
                if counterp == 3:
                    st.success(f'**{user_input} spec are met!**')
                    df.loc[df['asset_tag'] == user_input, 'date'] = c_date
                    df.loc[df['asset_tag'] == user_input, 'torque_value'] = result
                    df.loc[df['asset_tag'] == user_input, 'p_f'] = 'pass'
                    try:
                        df.to_csv(csv_file, index=False)
                        st.success(f'CSV file updated on: {today}')
                    except:
                        st.error('Could not save data, excel file open, please close and try again')
                    break
            else:
                result = str1
                hold2.append(str1)
                counterf += 1
                with open(os.path.join(aws_f, f'{user_input}.txt'), 'a') as file:
                    file.writelines([full_date, ' | ', 'fail', ' | ', user_input, ' | ', torque_id, ' | ', str1,])
                re_write.error(str1 + 'Fail')
                fail_image.image(toasty, caption='Toasty!', width=95)
                sleep(1.5)
                fail_image.empty()
                if counterf == 3:
                    st.warning(f'**{user_input} is out spec, please send to maintenance**')
                    df.loc[df['asset_tag'] == user_input, 'date'] = c_date
                    df.loc[df['asset_tag'] == user_input, 'p_f'] = 'fail'
                    df.loc[df['asset_tag'] == user_input, 'torque_value'] = result
                    try:
                        df.to_csv(csv_file, index=False)
                        st.success(f'CSV file updated on: {today}')
                    except:
                        st.error('Could not save data, excel file open, please close and try again')
                    break
        except ValueError:
            pass

#function to terminate connection to AWS
def stop_ser():
    ser = serial.Serial(port='COM6',
                        baudrate=9600,
                        timeout=2 
    )
    ser.close

def filtering1(df):
    pf = list(df['p_f'].unique())
    pffilter = st.sidebar.multiselect('Filter by Pass or Fail', pf)
    df1 = df[(df['p_f']).isin(pffilter)]

    if not pffilter:
        df
    else:
        df1




#SideBar-------------------------------------------------------------------------------------------------------------
st.sidebar.title('Asset Tag Number Menu')
# s_checkbox = st.sidebar.checkbox('App Menu')
# st.sidebar.subheader('Edit Dataframe')

#Torque Asset Info----------------------------------------------------------------------------------------------------
with main_column:
    st.title('**ZTSystems**')
    input_sidebar = st.empty()
    delete_ = st.empty()
    # if s_checkbox:
    st.title('Torque Asset Info')
    s_input = st.sidebar.text_input('Search Asset #')
    s_area = st.sidebar.text_area('Search Multiple Asset #')
        # st.write(filtering(df))

    if s_input == "":
        st.image(ztbanner)
        st.write('-------------------------------------') 
    elif s_input in df.values:
        st.write('Asset tag # Output:')
        st.write(df[df['asset_tag']==s_input])
        st.write('-------------------------------------')       
    else:
        st.write(f"Asset number: **{s_input}**, not in dataframe, check spelling. :sleuth_or_spy:")

    if s_area == "":
        pass
    elif s_area is not None:
        st.write('Multiple Asset tag # Output:')
        textsplit = s_area.splitlines()
        for i in textsplit:
            if i in df.values:
                st.write(df[df['asset_tag']==i])
            else:
                st.write(f"Asset number: **{i}**, not in dataframe, check spelling. :sleuth_or_spy:")
        st.write('-------------------------------------')
    st.sidebar.subheader('Filter Data: ')
    st.sidebar.subheader('Edit Dataframe')
    input_sidebar = st.sidebar.text_input('Asset # to delete:')
    delete_ = st.sidebar.button('Delete')
    if input_sidebar in df.values:
        if delete_:
            df.drop(df.index[(df['asset_tag'] == input_sidebar)], axis = 0, inplace = True)
            df.to_csv(csv_file, index=False)
            st.success(f'**{input_sidebar}** removed. :disappointed_relieved:')



#AWS Torque Tester---------------------------------------------------------------------------------------------------
with s_column:
    st.title('AWS Torque Tester')
    torque_id = st.text_input("Torque Tester Asset Tag:", max_chars=3, help='Scan Torque tester asset tag number :avocado:')

    if torque_id:
        user_input = st.text_input("Torque Asset #: ",  key='asset', help='Scan Asset # Here :man-man-girl:')
        st.subheader('Torque Value in N-m:')
        if user_input:
            pass

        if st.button('Test Torque'):
            run()

        if st.button('Close Connection'):
            stop_ser()


#Data viewer---------------------------------------------------------------------------------------------------------
with t_column:
    st.title('Torque Asset Data')
    st.text('Asset Tag Torque Information:')
    del_text = st.empty()
    br = df['brand'].drop_duplicates().sort_values()
    nm = df['nominal_torque'].drop_duplicates().sort_values()
    location = df['location'].drop_duplicates().sort_values()
    
    #user input------------------------------------------------------------------------------------------------------
    try:
        if user_input in df.values:
            st.write(df[df['asset_tag']==user_input])
        elif user_input == '':
            st.write('Type in an Asset Tag #')
        elif user_input not in df:
            del_text.write(f"Asset number: **{user_input}**, not in dataframe, check spelling. :sleuth_or_spy:")

            # if st.button('Save'):
            #     try:
            #         df.to_csv(csv_file, index=False)
            #         st.success(f'CSV file updated on: {today}')
            #     except ValueError:
            #         st.error('CSV file is open by another program, please close that program (excel...)') 
    except:
        pass

   
            
#Dataframe----------------------------------------------------------------------------------------------------------
st.text('Dataframe:')
try:
    st.write(filtering1(df))
except:
    pass
#--------------------------------------------------------------------------------------------------------------------

