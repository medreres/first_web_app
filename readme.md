**Revista**
#### Video Demo:  <https://youtu.be/7XAisu6pYUM>
#### Description:
### profile(), login(), validate(), register() use SQL databse in order to check information on user
#### There is another database "grades" which provide information about who gave the grade, the student, and the subject
### some functions, like "apology" were stolen from last CS50 project, because i liked them very much ;)
### funct homepage() juft return rendered page "homepage.html" which is quite simple, similarly does contacts(), and timetable()
### function login() connects to database and searches user with particular features, login can take as much as username or email
### logout() clears all the session data
### register() turns to database to check whether email or username is already used, sends code to entered email, then passes some values to validate()
### validate compares codes sent and entered, allowing user to go on using the website