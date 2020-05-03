#Import Flask Library
from flask import Flask, render_template, request, session, url_for, redirect,flash
from werkzeug.utils import secure_filename
import hashlib
import os
import pymysql.cursors
SALT = 'cs3083'
ALLOWED_EXTENSIONS = set(['png','jpg','jpeg','gif','bmp'])





#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       port = 8889,
                       user='root',
                       password='root',
                       db='Finstagram',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

#check file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#get visible photos
def get_visible(username):
    cursor = conn.cursor();

    query = 'SELECT postingDate, pID, firstName,lastName,filePath FROM Photo JOIN Follow ON(poster = followee) JOIN Person ON(poster = username) WHERE follower = %s AND allFollowers = 1 AND followStatus = 1 UNION (SELECT postingDate, pID, firstName,lastName,filePath FROM Photo JOIN Person ON(poster = Person.username) WHERE pID IN (SELECT pID FROM SharedWith NATURAL JOIN BelongTo WHERE username = %s)) UNION(SELECT postingDate, pID, firstName,lastName,filePath FROM Photo JOIN Person ON(poster = Person.username) WHERE poster = %s)ORDER BY postingDate DESC'
    cursor.execute(query, (username, username, username))

    data = cursor.fetchall()
    cursor.close()
    return data

#Define a route to hello function
@app.route('/')
def hello():
    return render_template('index.html')

#Define route for login
@app.route('/login')
def login():
    return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
    return render_template('register.html')

#Authenticates the login
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']+SALT
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE username = %s and password = %s'
    cursor.execute(query, (username, hashed_password))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    cursor.close()
    error = None
    if(data):
        #creates a session for the the user
        #session is a built in
        session['username'] = username
        return redirect(url_for('home'))
    else:
        #returns an error message to the html page
        error = 'Invalid login or username'
        return render_template('login.html', error=error)

#Authenticates the register
@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
    #grabs information from the forms
    username = request.form['username']
    password = request.form['password']+SALT
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    fname = request.form['fname']
    lname = request.form['lname']
    email = request.form['email']

    #cursor used to send queries
    cursor = conn.cursor()
    #executes query
    query = 'SELECT * FROM Person WHERE username = %s'
    cursor.execute(query, (username))
    #stores the results in a variable
    data = cursor.fetchone()
    #use fetchall() if you are expecting more than 1 data row
    error = None
    if(data):
        #If the previous query returns data, then user exists
        error = "This user already exists"
        return render_template('register.html', error = error)
    else:
        ins = 'INSERT INTO Person VALUES(%s, %s, %s, %s, %s)'
        cursor.execute(ins, (username, hashed_password, fname,lname,email))
        conn.commit()
        cursor.close()
        return render_template('index.html')

#route for homepage
@app.route('/home')
def home():
    try:
        username = session['username']
    except:
        error = 'Cannot find existing session. Please log in.'
        return render_template('login.html', error=error)
    data = get_visible(username)
    return render_template('home.html', username=username, posts=data)
#route for tag information
@app.route('/tag_info/<pID>')
def tag_info(pID):
    try:
        username = session['username']
    except:
        error = 'Cannot find existing session. Please log in.'

    query = 'SELECT username, firstName,lastName FROM Tag NATURAL JOIN Person WHERE pID = %s AND tagStatus = 1'

    cursor = conn.cursor()
    cursor.execute(query,(int(pID)))
    data = cursor.fetchall()
    cursor.close()

    return render_template('tag_info.html',pID = pID, posts = data)

#route for reaction info
@app.route('/react_info/<pID>')
def react_info(pID):
    try:
        username = session['username']
    except:
        error = 'Cannot find existing session. Please log in.'

    query = 'SELECT username, comment, emoji FROM ReactTo WHERE pID = %s'

    cursor = conn.cursor()
    cursor.execute(query,(int(pID)))
    data = cursor.fetchall()
    cursor.close()

    return render_template('react_info.html',pID = pID, posts = data)

#route for create group
@app.route('/createGroup')
def create_group():
    try:
        username = session['username']
    except:
        error = 'Cannot find existing session. Please log in.'
        return render_template('login.html', error=error)

    return render_template('create_group.html')

@app.route('/createAuth', methods=['GET', 'POST'])
def createAuth():
    try:
        username = session['username']
    except:
        error = 'Cannot find existing session. Please log in.'
        return render_template('login.html', error=error)
    #get user input from from
    groupName = request.form['groupName']
    description = request.form['description']

    cursor = conn.cursor()
    query = 'SELECT * FROM FriendGroup WHERE groupName = %s AND groupCreator = %s'
    cursor.execute(query, (groupName,username))
    data = cursor.fetchone()
    error = None
    if(data):
        #If the previous query returns data, then the group has already been created
        error = "This group already exists"
        return render_template('create_group.html', error = error)
    else:
        #create new group
        create_query = 'INSERT INTO FriendGroup VALUES(%s, %s,%s)'
        #add the creator as a member to the new group
        belong_query = 'INSERT INTO BelongTo VALUES(%s, %s,%s)'
        cursor.execute(create_query,(groupName, username, description))
        cursor.execute(belong_query,(username,groupName,username))
        conn.commit()
        cursor.close()
        return redirect(url_for('home'))

#route for post photo
@app.route('/post', methods=['GET', 'POST'])
def post():
    try:
        username = session['username']
    except:
        error = 'Cannot find existing session. Please log in.'
        return render_template('login.html', error=error)
    if request.method == 'POST':
        #get user input from the webpage
        file = request.files['file']
        caption = request.form['caption']
        shared_groups = request.form.getlist('shared_groups')
        all_followers = int(request.form['all_followers'])

        #check whether the file type is photo
        if file and allowed_file(file.filename):
            # save photo to a dedicated folder
            basepath = os.path.dirname(__file__)
            upload_path = os.path.join(basepath,'static/images', secure_filename(file.filename))
            file.save(upload_path)


            cursor = conn.cursor();
            photo_query = 'INSERT INTO Photo (postingDate,allFollowers,caption,poster) VALUES(NOW(),%s,%s,%s)'
            shared_with_query = 'INSERT INTO SharedWith (pID,groupName,groupCreator)VALUES(LAST_INSERT_ID(),%s,%s)'
            update_path = 'UPDATE Photo SET filePath = %s WHERE pID = %s'
            #insert info to Photo
            cursor.execute(photo_query, (all_followers, caption, username))

            #rename file as pID and upload filrpath
            extension = file.filename.rsplit('.', 1)[1].lower()

            get_ID = 'SELECT LAST_INSERT_ID() AS pID FROM Photo'
            cursor.execute(get_ID)

            pID = cursor.fetchone()['pID']
            filePath = str(pID)+'.'+extension
            cursor.execute(update_path,(filePath,pID))

            os.rename(upload_path,os.path.join(basepath,'static/images',str(pID)+'.'+extension))


            #update sharedWith
            for i in shared_groups:
                group = i.split(',')
                groupName = group[0]
                groupCreator = group[1]
                cursor.execute(shared_with_query,(groupName,groupCreator))
            conn.commit()
            cursor.close()
            return redirect(url_for('home'))
        else:
            flash('Error: No file or the file type is not supported')
            return redirect(url_for('post_photo'))


@app.route('/post_photo')
def post_photo():
    try:
        username = session['username']
    except:
        error = 'Cannot find existing session. Please log in.'
        return render_template('login.html', error=error)
    cursor = conn.cursor();
    query = 'SELECT DISTINCT groupName, groupCreator FROM BelongTo WHERE username = %s'
    cursor.execute(query,(username))
    groups = cursor.fetchall()
    cursor.close()
    return render_template('post_photo.html',groups = groups)

#route for manage tags
@app.route('/manage_tags')
def manage_tags():
    try:
        username = session['username']
    except:
        error = 'Cannot find existing session. Please log in.'
        return render_template('login.html', error=error)
    data = get_visible(username)
    return render_template('manage_tags.html', posts=data)

#route for create tag request
@app.route('/create_tag',methods=['GET', 'POST'])
def create_tag():
    try:
        username = session['username']
    except:
        error = 'Cannot find existing session. Please log in.'
        return render_template('login.html', error=error)

    
    pID = int(request.form["pID"])
    target = request.form['target']

#see whether the tag request already exists (to avoid violating primary key restriction)
    exist_query = 'SELECT * FROM Tag WHERE pID = %s AND username = %s'
    cursor = conn.cursor()
    cursor.execute(exist_query,(pID,target))
    exist = cursor.fetchone()
    if exist:
        data = get_visible(username)
        flash('This user has already beem tagged')
        return render_template('manage_tags.html', posts=data)

    add_query = 'INSERT INTO Tag VALUES(%s,%s,%s)'
    visible_query = 'SELECT pID FROM Photo JOIN Follow ON(poster = followee) JOIN Person ON(poster = username) WHERE follower = %s AND allFollowers = 1 AND followStatus = 1 AND pID = %s UNION (SELECT pID FROM Photo JOIN Person ON(poster = Person.username) WHERE pID = %s AND pID IN (SELECT pID FROM SharedWith NATURAL JOIN BelongTo WHERE username = %s))UNION(SELECT pID FROM Photo JOIN Person ON(poster = Person.username) WHERE poster = %s)'
    valid_target_query = 'SELECT * FROM Person WHERE username = %s'
    #whether the target exist
    cursor = conn.cursor()
    
    cursor.execute(valid_target_query, (target))
    valid_target = cursor.fetchone()


    #whether the photo is visible to the target

    cursor.execute(visible_query,(target,pID,pID,target,target))
    visible = cursor.fetchone()
    cursor.close()


    
    if (valid_target):
        cursor = conn.cursor()
        #self-tagging, status = 1
        if target == username:
            cursor.execute(add_query,(pID,username,1))
            flash('Tag added!')
        #tag pending, status = 0
        elif visible:
            cursor.execute(add_query,(pID,target,0))
            flash('Tag request sended,status: pending')
        #photo is not visible to the target
        else:
            flash('Error: Tag failed. The photo is not visible to the user.')
    #target does not exist
    else:
        flash('Error: Tag failed. The username does not exist.')
    conn.commit()
    cursor.close()
    data = get_visible(username)
    return render_template('manage_tags.html', posts=data)

#handle pending tags
@app.route('/pending_tags')
def pending_tags():
    try:
        username = session['username']
    except:
        error = 'Cannot find existing session. Please log in.'
        return render_template('login.html', error=error)

    get_tag_query = 'SELECT pID, filePath, firstName, lastName, postingDate FROM (Tag JOIN Photo USING (pID)) JOIN Person ON(Person.username = Photo.poster) WHERE Tag.username = %s AND tagStatus = 0'
    cursor = conn.cursor()
    cursor.execute(get_tag_query,(username))
    data = cursor.fetchall()
    cursor.close()
    return render_template('pending_tags.html', posts=data)

@app.route('/handle_tag_request',methods=['GET', 'POST'])
def handle_tag_request():
    try:
        username = session['username']
    except:
        error = 'Cannot find existing session. Please log in.'
        return render_template('login.html', error=error)
    
    pID = int(request.form["pID"])
    action = request.form["action"]


    get_tag_query = 'SELECT pID, filePath, firstName, lastName, postingDate FROM (Tag JOIN Photo USING (pID)) JOIN Person ON(Person.username = Photo.poster) WHERE Tag.username = %s AND tagStatus = 0'
    accept_query = 'UPDATE Tag SET tagStatus = 1 WHERE username = %s AND pID = %s'
    decline_query = 'DELETE FROM Tag WHERE username = %s AND pID = %s'

    cursor = conn.cursor()
    if action == "Accept":
        cursor.execute(accept_query,(username,pID))
        flash('Tag request accepted!')
    elif action =="Decline":
        cursor.execute(decline_query,(username,pID))
        flash('Tag request declined!')

    conn.commit()
    cursor.execute(get_tag_query,(username))
    data = cursor.fetchall()
    cursor.close()

    return render_template('pending_tags.html', posts=data)
        

#---------------------Yi Zheng update: Manage Follow function------------------------------------

@app.route('/ManageFollow', methods=['GET', 'POST'])
def ManageFollow():
    username = session['username']
    cursor = conn.cursor()
    query = 'SELECT follower FROM Follow WHERE followee = %s AND followStatus = %s'
    cursor.execute(query, (username, 0))
    data = cursor.fetchall()
    return render_template('ManageFollow.html',username=username, Request=data)

@app.route('/AcceptOrReject', methods=['GET','POST'])
def AcceptOrReject():
    username = session['username'] #followee
    cursor = conn.cursor()
    follower= request.form['AcceptOrReject'] #follower
    Accept = None
    Reject = None
    try:
        Accept = request.form['Accept']
    except:
        Reject = request.form['Reject']
    if Accept:
        query = 'UPDATE Follow SET followStatus = %s WHERE followee = %s AND follower = %s'
        cursor.execute(query, (1, username, follower))
        conn.commit()
        cursor.close()
        return render_template('ManageFollow.html')
    if Reject:
        query = 'DELETE FROM Follow WHERE followee = %s AND follower = %s'
        cursor.execute(query,(username, follower))
        conn.commit()
        cursor.close()
        return render_template('ManageFollow.html')

    error = 'Error'
    return render_template('ManageFollow.html', error=error)

@app.route('/RequestFollow', methods=['GET', 'POST'])
def RequestFollow():
    username = session['username']
    cursor = conn.cursor()
    followee = request.form['followname']

    if username == followee:
        error = 'You cannot follow yourself'
        return render_template('ManageFollow.html', error=error)

    #check whether followee has been followed

    query = 'SELECT username FROM Person WHERE username = %s'
    cursor.execute(query,(followee))
    data1 = cursor.fetchone()
    #If this person not in the database
    if not data1:
        error = 'This guy is not registered'
        return render_template('ManageFollow.html', error=error)

    query = 'SELECT followee FROM Follow WHERE follower = %s AND followee = %s'
    cursor.execute(query, (username, followee))
    data2 = cursor.fetchone()

    if data2: # check if has sent a request
        error = "You have followed this person or your request is pending."
        cursor.close()
        return render_template('ManageFollow.html', error=error)
    else: #sent a requset
        query = 'INSERT INTO Follow(follower, followee, followStatus) VALUES (%s, %s, %s)'
        cursor.execute(query,(username, followee, 0))
        conn.commit()
        cursor.close()
        message = 'Your request has been sent.'
        return render_template('ManageFollow.html', message=message)

@app.route('/Unfollow', methods=['GET', 'POST'])
def Unfollow():
    username = session['username']
    cursor = conn.cursor()
    followee = request.form['followname']

    #Check whether this guy is being followed
    query = 'SELECT followee FROM Follow WHERE follower = %s AND followee = %s'
    cursor.execute(query, (username, followee))
    data1 = cursor.fetchone()
    # If this person not in the database
    if username == followee:
        error = 'You cannot unfollow yourself'
        return render_template('ManageFollow.html', error=error)
    if not data1:
        error = 'You are not following this person please try another name'
        return render_template('ManageFollow.html', error=error)
    query = 'DELETE FROM Follow WHERE follower = %s AND followee = %s'
    cursor.execute(query, (username, followee))
    print(1)
    conn.commit()
    cursor.close()
    message = 'You have unfollowed ' + followee + '.'
    return render_template('ManageFollow.html', message=message)



@app.route('/AddFriend', methods=['GET', 'POST'])
def AddFriend():
    return render_template('AddFriend.html')

@app.route('/Add_or_Delete', methods=['GET', 'POST'])
def Add_or_Delete():
    username = session['username']
    groupname = request.form['groupname']
    friendname = request.form['friendname']
    Add = None
    Delete = None
    try:
        Add = request.form['Add']
    except:
        Delete = request.form['Delete']
    cursor = conn.cursor()

    #check the existence of friendgroup and user
    #check the existence of the friendgroup
    query = 'SELECT * FROM FriendGroup WHERE groupName = %s AND groupCreator = %s'
    cursor.execute(query, (groupname, username))
    data = cursor.fetchone()
    if not data:
        error = "This friendgroup doesn't exist."
        return render_template('AddFriend.html', error=error)
    #check the existence of the user
    query = 'SELECT * FROM Person WHERE username=%s'
    cursor.execute(query, (friendname))
    data = cursor.fetchone()
    if not data:
        error = "This user doesn't exist."
        return render_template('AddFriend.html', error=error)


    #check whether friend is already in the friendgroup
    query = 'SELECT username FROM BelongTo WHERE username = %s'
    cursor.execute(query, (friendname))
    data = cursor.fetchone()

    error = None
    if Add:
        if data:
            print(1)
            error = 'Your friend is already in the group'
            cursor.close()
            return render_template('AddFriend.html', error=error)
        else:
            query = 'INSERT INTO BelongTo (username, groupName, groupCreator) VALUES (%s, %s, %s)'
            print(1)
            cursor.execute(query, (friendname, groupname, username))
            conn.commit()
            cursor.close()
            message = "You has successfully add a friend."
            return render_template('AddFriend.html', message= message)
    if Delete:
        if data:
            query = 'DELETE FROM BelongTo WHERE groupName = %s AND groupCreator = %s AND username = %s'
            cursor.execute(query,(groupname, username, friendname))
            message = "Your friend has been deleted"
            cursor.close()
            return render_template('AddFriend.html', message=message)
        else:
            error = friendname + " is not in the friendgroup."
            cursor.close()
            return render_template('AddFriend.html', error = error)



#------------------------------------Yi Zheng update end---------------------------------


# search by tag
@app.route('/search_by_tag')
def search_by_tag():
    return render_template('search_by_tag.html')


@app.route('/search_by_tag_auth', methods=['GET', 'POST'])
def search_by_tag_auth():
    user = session['username']
    tag = request.form['tag']
    cursor = conn.cursor();

    query = '''SELECT DISTINCT postingDate, ph.pID, firstName,lastName,filePath FROM (Photo AS ph JOIN Person AS p ON(p.username = ph.poster)) JOIN Tag AS t USING(pID) WHERE(ph.poster = %s AND t.username = %s) OR (allFollowers = 1 AND %s IN (SELECT follower FROM Follow WHERE followee = ph.poster AND followStatus = 1) AND t.username = %s) OR (allFollowers = 0 AND %s IN (SELECT username FROM BelongTo WHERE (groupName, groupCreator) IN (SELECT groupName, groupCreator FROM SharedWith WHERE pID = ph.pID)) AND t.username = %s) ORDER BY postingDate DESC'''

    cursor.execute(query, (user, tag, user, tag, user, tag))

    data = cursor.fetchall()
    # print(data)
    cursor.close()
    error = None
    if (data):
        return render_template('search_results_tag.html', username=user, tag=tag, posts=data)
    else:
        # returns an error message to the html page
        error = 'Invalid search'
        return render_template('search_by_tag.html', error=error)


# search by poster
@app.route('/search_by_poster')
def search_by_poster():
    return render_template('search_by_poster.html')


@app.route('/search_by_poster_auth', methods=['GET', 'POST'])
def search_by_poster_auth():
    user = session['username']
    poster = request.form['poster']
    cursor = conn.cursor();

    query = '''
    SELECT postingDate, pID, firstName, lastName, filePath, poster FROM Photo AS ph JOIN Person AS p ON(p.username = ph.poster) WHERE (ph.poster = %s AND ph.poster = %s) OR (allFollowers = 1 AND %s IN (SELECT follower FROM Follow WHERE followee = ph.poster AND followStatus = 1) AND ph.poster = %s) OR (allFollowers = 0 AND %s IN (SELECT username FROM BelongTo WHERE (groupName, groupCreator) IN (SELECT groupName, groupCreator FROM SharedWith WHERE pID = ph.pID)) AND ph.poster = %s) ORDER BY postingDate DESC
    '''

    cursor.execute(query, (user, poster, user, poster, user, poster))

    data = cursor.fetchall()
    # print(data)
    cursor.close()
    error = None
    if (data):
        return render_template('search_results_poster.html', username=user, poster=poster, posts=data)
    else:
        # returns an error message to the html page
        error = 'Invalid search'
        return render_template('search_by_poster.html', error=error)




@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/')
        
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)
