## Project Purpose

Provide User a platform for sharing idea and communication
<br />
<br />
<br />

## How to deploy on Google App Engine
<br />
1. Based on instructions on <a href="https://multiuserblog-163505.appspot.com">QuickStart</a>,
go to the <a href="https://console.cloud.google.com/start">Cloud Platform Console</a> to create
a new project after selecting<br /> &emsp;google account to login<br />
2. After giving the project a name, a unique project ID is created on the line below<br />
3. Wait for 30 seconds for the project to be initialized<br />
4. Install appropriate Google Cloud SDK package from
<a href="https://cloud.google.com/sdk/docs/#mac">Here(Default Mac)</a><br />
5. Run the install script "install.sh" to add the GCS tools to your path<br />
6. Start a new terminal<br />
7. Go to the project folder and run the following command to configure the gcloud:<pre>gcloud init</pre>
8. Within the project folder, type the following command to test on localhost:<pre>dev_appserver.py .</pre>
After that, the local page can be accessed at <a href="http://localhost:8080">http://localhost:8080</a><br /><br />
9. Finally, deploy the app to the cloud so anyone in the world can view it:<pre>gcloud app deploy</pre>
10. Type in the following command to open the public URL of the project:<pre>gcloud app browse</pre>
<br />

## How to use the website:

<a href="https://multiuserblog-164902.appspot.com">https://multiuserblog-163505.appspot.com</a><br />
Click the link above to access the main page. After that you need
to create an account and login. Then you will see others' posts and
you can also make new posts or reply to other people's posts. Additionally,
you are able to edit you own posts and comments. After logout, you need to
re-enter the username and passward to login again.


#### Tips: If you want to edit your post, just click on the title in blue, be
aware that you can only change your own staff. If you want to change your conment,
just click on it!


<br />
<br />

##### Notice:
After accessing the main page, you will be lead to different pages
based on your action. There is no need to manually type a specific address

