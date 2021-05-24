# Datagran interview question #2

This is an API developed with **Flask**, **MongoDB** and can be runned locally or using **docker**. It's objective is to receive bash commands, execute them in the background and report the command's results.

## Running the application using Docker and Docker Compose

First you need to have installed Docker and Docker Compose. I have used the versions:

Docker version 20.10.6, build 370c289

docker-compose version 1.21.2, build a133471

To run the application, simply open a terminal in the same directory as this readme, and execute:

**docker-compose up**

**NOTE**: if your user is not in the docker group, you will need to run the command using sudo

There are two containers, one for the API and another for the DB. Wait until both are up

Then you can access the API via the address **http://localhost:5000/**

## API specification

### 1) Request to save and execute a new command

To do this, you should perform a POST request to http://localhost:5000/new_task 
with a json body like the following:

{
	"cmd":"mkdir ori2"
}

If successfully created the task, a 200 status code is returned with a json response including the id of the command saved to the DB:

{
  "id": "60abc199dba2de42560f1a67"
}

If "cmd" is missing in the json body, a 400 status code is returned with the following response:

{
  "error": "COMMAND_MISSING"
}

If there is any other unlikely error, the server will return a 500 status with the following response:

{
  "error": "INTERNAL_ERROR"
}

### 2) Request to get command execution status and output

To do this, you should perform a GET request to http://localhost:5000/get_output/{taskId} where {taskId} is the id returned from the POST request

If the ID is valid and exists in the db, a 200 status code is returned with a json response including the command, it's output and the state in which it finished, for example:

{
  "cmd": "mkdir test",
  "output": "",
  "state": "FINISHED_OK"
}

There are 4 different states for a command:

  NOT_STARTED = The command isn't executing yet.

  STARTED = The command has started it's 

  NOT_EXECUTED = The command wasn't executed (This could happen because it's an invallid command, for example if we try to execute 'asd') 

  FINISHED_OK = The command executed succesfully

  FINISHED_ERROR = The command could be executed, but there was an error during the execution. For example if we run two times 'mkdir test', the second time it will fail, because it already exists

**NOTE** I decided to include a state in this response because the output itself could be very little information sometimes. In this example, the command executed doesnt have any output from the STDERR or STDOUT and it could be confusing, we could wonder if it was executed or not.

If the id is valid but doesnt exist in the db, a 404 status code is returned with the following json response:

{
  "error": "TASK_NOT_FOUND"
}

If the id is invalid, a 400 status code is returned with the following json response:  

{
  "error": "INVALID_ID"
}

**Author**: [Tomas Eduardo Pinto](https://github.com/pintotomas)