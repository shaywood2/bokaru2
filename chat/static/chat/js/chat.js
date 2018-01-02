initializeSession()

// Handling all of our errors here by alerting them
function handleError(error) {
    if (error) {
        alert('Oops, seems like something went wrong: ' + error.message)
    }
}

function initializeSession() {
    var session = OT.initSession(window.apiKey, window.sessionId)

    // Subscribe to a newly created stream
    session.on('streamCreated', function(event) {
        session.subscribe(event.stream, 'remote_video', {
            insertMode: 'append',
            fitMode: 'contain',
            width: '100%',
            height: '100%'
        }, handleError)
    })

    session.on({
        streamDestroyed: function (event) {
            console.log("Stream stopped. Reason: " + event.reason)
            if (event.reason === 'networkDisconnected') {
                event.preventDefault()
                var subscribers = session.getSubscribersForStream(event.stream)
                if (subscribers.length > 0) {
                    var subscriber = document.getElementById(subscribers[0].id)
                    // Display error message inside the Subscriber
                    subscriber.innerHTML = 'Lost connection. This could be due to your internet connection '
                    + 'or because the other party lost their connection.'
                    event.preventDefault()   // Prevent the Subscriber from being removed
                }
            } else if (event.reason === 'clientDisconnected') {
                event.preventDefault()
                var subscribers = session.getSubscribersForStream(event.stream)
                if (subscribers.length > 0) {
                    var subscriber = document.getElementById(subscribers[0].id)
                    // Display error message inside the Subscriber
                    //subscriber.innerHTML = 'k thx bye'
                    event.preventDefault()   // Prevent the Subscriber from being removed
                }
            }
        }
    })

    // Create a publisher
    var publisher = OT.initPublisher('local_video', {
        insertMode: 'append',
        fitMode: 'contain',
        width: '100%',
        height: '100%'
    }, handleError)

    publisher.on("streamDestroyed", function (event) {
        console.log("Stream stopped. Reason: " + event.reason)
    })

    // Connect to the session
    session.connect(window.token, function(error) {
        // If the connection is successful, publish to the session
        if (error) {
            handleError(error)
        } else {
            session.publish(publisher, handleError)
        }
    })
}

function takeSnapshot() {
    var imgData = publisher.getImgData();
    var img = document.createElement("img");
    img.setAttribute("src", "data:image/png;base64," + imgData);
}

function reportIssue() {
    OT.reportIssue(function(error, issueId) {
        if (error) {
            console.log(error)
        } else {
            console.log(issueId);
            // You may want to use XMLHttpRequest to report this issue ID to a server
            // that can store it in a database for later reference.
        }
    })
}
