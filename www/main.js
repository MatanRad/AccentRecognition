var isRecording = false, encode = false;
var wsh = new WebSocket( 'ws://127.0.0.1:8888/ws' );

var countries = null;

// Shows probabilities for each class
function BuildClassProbs(probs)
{
    var s = "";
    for (var i=0; i < countries.length; i++)
    {
        s += countries[i] +": "+probs[i].toString().substring(0, 5)+"<br>";
    }
    document.getElementById("probs").innerHTML = s;
}

// On receive message from stream websocket
function onWsMessage( msg )
{ 
    console.log(msg.data);
    // if countries is null we need to initialize our probabilities and countries. Also display placeholder dots.
    if (countries != null)
    {
        var y;
        var spl = msg.data.split(';');
        y = parseInt(spl[0]);
        document.getElementById("accent").innerHTML = countries[y]
        BuildClassProbs(JSON.parse(spl[1]));
    } 
    else
    {
        if(msg.data.length > 1)
        {
            probs = []
            countries = JSON.parse(msg.data);

            for (var i=0; i < countries.length; i++)
            {
                probs.push("...");
            }

            BuildClassProbs(probs);
            console.log("Initialized");
        }
    }
}

// define media handler for mic input.
wsh.onmessage = onWsMessage;
var ap = new OpusEncoderProcessor( wsh );
var mh = new MediaHandler( ap );

// send the settings our code is running with to the client.
function sendSettings()
{
	encode = 0;

    var rate = String( mh.context.sampleRate / ap.downSample );
    var opusRate = String( ap.opusRate );
    var opusFrameDur = String( ap.opusFrameDur )

    var msg = "m:" + [ rate, encode, opusRate, opusFrameDur ].join( "," );
    console.log( msg );
    wsh.send( msg );
}

// start recording mic input
function startRecord()
{
    document.getElementById( "record").innerHTML = "Stop";
    sendSettings();
    isRecording = true;
    console.log( 'started recording' );
    working = true;
}

// pause mic input
function stopRecord()
{
    isRecording  = false;
    document.getElementById( "record").innerHTML = "Record";
    console.log( 'ended recording' );    
    working = false;
}

// toggle mic input.
function toggleRecord()
{
    if( isRecording )
	stopRecord();
    else
	startRecord();
}
