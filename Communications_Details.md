# Mirrulations Server/Client Communication
## Server Communication

### Client

* Activated by `GET` call to the `/get_work` endpoint 
* Given:
  * Running server
  * Redis database with a `linked list` representing the jobs that are `queued`
      - `queued` list contains: `job data`, `job type`, `job id`
  * Redis database with a `hash set` representing the `in progress jobs`
  * `Client_ID` of the user requesting work
  * Current `version number` of the system
* If:
  * User makes a successful call to the server 
  * There is work to be done
* Then: `LOG EVERYTHING`
  * Fetch a job from the `queued` linked list
  * Create a json to send as a task
	<pre><code>
{"job\_id":str,             |    {"job\_id":str,
 "job\_type":"__doc__",          |     "job\_type":"__docs__",
 "data":[{"id":"...",       |     "data":[{"url":...},
          "AtCom":int},...         |             {"crl":...}],
        ],                         |     "version":"v1.0",
        						   |	 "client\_id": "...",
 "version":"v1.0",          |    }
 "client\_id": "..."         |
}                          |
	</code></pre>
  * Return the json as a successful response
  * Add timestamp to data
  * Move job from `queued` to `in progress`

### Filter

* Docs:
  * Returned JSON looks like:
	<pre><code>
{"job\_id": xx-123,
 "data":[
         [ (1 workfile)
          {"id":...
           "count":...
           }
          ...
         ],
         [ (another workfile)
          {"id":...
           "count":...
           }
          ...
         ],
        ]
 "version":"v1.0"
}
</code></pre>
  * Loop through the `"data"` entry in the json - List of lists
  * Each entry in `"data"` contains entries with at most 1000 counts
  * If valid, loop through list of ids in `"data"`
  * Add list of document ids to the `queued` list
* Doc:
  *  Returned JSON looks like
	<pre><code>
{"job\_id": xx-123,
"data":[
         [ (1 workfile)
          {"id":...
           "count":...
           }
          ...
         ],
         [ (another workfile)
          {"id":...
           "count":...
           }
          ...
         ],
        ]
 "version":"v1.0"
}
	</code></pre>
  * Check formating of the documents `doc.ID.*`
  * Check that the last part of the `ID` is a number
  * When a `.json` is found, check if the ID inside the json is the same as the filename
  * If valid, make place for storage
	<pre><code>- organization
			- docket ID
			  - document ID
			    - files
	</code></pre>
  * Save the file to the local directory

  
### Expiration

* Runs every *hour*
* Loop through the `in progress` hash stored in the Redis database
* Check if the timestamp on the job is older than *6 hours*
* Move task from `in progress` to `queued`


## Client Communication

### Server

* Client makes a call to the server using `/get_work` endpoint
* Server returns json
    * `type` used to determine whether client moves forward using `documents_processor` or `document_processor`

#### Documents Processor
* Given: 
    * A list of urls from the `data` field of the returned json from `/get_work`
* Responses:
    * `200` - Returns json containing the fields `job_id`, `type`, `data`, and `version`   
    * `300` - A temporary error occured and the call will retry
    * `400` - A bad request was made 
* Following a `200` response:
	* Using each url in the list, the client will make a call to the regulations api and compile a list of document IDs
	*  Once the document IDs are obtained, it will call the `work_accumulator` and save them as a `workfile` list
	*  The client will then make a call to the api using `/return_docs`, using the `workfile` list as data passed

#### Document Processor
* Given: 
    * The `workfile` list from the `data` field of the returned json from `/get_work`
* Responses:
    * `200` - Returns the json containing the fields `job_id`, `data`, `type`, and `version`   
    * `300` - A temporary error occured and the call will retry
    * `400` - A bad request was made

* Following a `200` response:
	* For each of the document IDs in the list, the Client will make a call to regulations api and download the appropriate files (json, pdf, tiff, etc.)
	* Some of the document IDs will have extra files attached to them, so those will be downloaded next. 
	* The Client compresses all of the downloaded files
	* The Client will then make a call to the api using `/return_doc`, sending the compressed files as the data 








