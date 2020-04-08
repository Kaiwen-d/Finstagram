For Part 3 of the project, we completed the following features:
1) view visible photos
    As the user logged in, there will be a table on the homepage showing photos that are visible to him/her, in reverse chronological order.
    related function in Finstagram.py: home()
    
2) view further photo info
    This feature is included in the result of "view visible photos", postingDate, name of the poster are shown together with the pID. For each visible photo, we put a link in the table which direct to the file. The photo is stored in a designated directory: static/ images/
    Note: tag and reactTo feature are not implemented. We will add these info later.
    related function: home()
     
3) Post a photo
    Instead asking the user to enter the location of a photo on the client computer, we let the user to choose file and upload it. Also, the user can decide whether the photo is visible to all followers and which group to share with. The file will be saved in a designated directory: static/ images/, with the pID as filename.
    related function: post(),post_photo()
    
4) add friend group
    user can create friend groups. If the group has already been created, it will throw an  error massage "Error: This group already exists". Otherwise, the group will be created and Finstagram adds the creator as a group member.
    related function:create_group(),createAuth()
    
5) registrate and log in
    related functions:login(),register(),loginAuth(),registerAuth(). Note: the password will be hashed and stored in the database.
    
    

