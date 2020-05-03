The project Finstagram has the following features. We listed the related functions for each feature.

Required features:
1) view visible photos
    As the user logged in, there will be a table on the homepage showing photos that are visible to him/her, in reverse chronological order.
    related function in Finstagram.py: home()
    
2) view further photo info
    This feature is included in the result of "view visible photos", postingDate, name of the poster are shown together with the pID. For each visible photo, we put a link in the table which direct to the file. Also, there are links for tag information and reaction information. The photo is stored in a designated directory: static/ images/
    Note: tag and reactTo feature are not implemented. We will add these info later.
    related function: home(), tag_info(pID), react_info(pID)
     
3) Post a photo
    Instead asking the user to enter the location of a photo on the client computer, we let the user to choose file and upload it. Also, the user can decide whether the photo is visible to all followers and which group to share with. The file will be saved in a designated directory: static/ images/, with the pID as its filename.
    related function: post(),post_photo()
    
4) add friend group
    user can create friend groups. If the group has already been created, it will throw an  error massage "Error: This group already exists". Otherwise, the group will be created and Finstagram adds the creator as a group member.
    related function:create_group(),createAuth()

5) manage follow
    User can send follow request to another user and respond to the pending follow request.
    related function: ManageFollow(), AcceptOrReject(), RequestFollow().
    
6) registrate and log in
    related functions:login(),register(),loginAuth(),registerAuth(). Note: the password will be hashed and stored in the database.
    
Additional features:
Kaiwen Dai
manage tags(count for two features):
    Users can send requests to tag another user to a photo. Finstagram should throw error if the target is not a registerd user, or the photo is not visible to the target, or the target has already been tagged. In the case of self-tagging, the user will be tagged immediately. If the user is tagging another user, a pending request will be sent. The taggee will have a chance to accept it or reject it.
    related functions: manage_tags(), create_tag(), pending_tags(), handle_tag_request()
    
Richard Zheng:
Unfollow:
    Users can unfollow another user. Should throw exception if: 1.unfollow oneself. 2. user does not exist
    related functions: Unfollow()
Add friend:
    Add friends to groups
    related functions: AddFriend(), Add_or_Delete()
    
Lily Yu:
Search by tag:
    search photos by tag. Should throw exceptions if the there's no tag with the search target.
    related functions: search_by_tag(), search_by_tag_auth()
    
Search by user:
    search photos by poster. should throw exceptions if the poster does not exist.
    related functions: search_by_poster(), search_by_poster_auth()
    
  

