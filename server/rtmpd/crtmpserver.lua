configuration=
{
	daemon=false,
	pathSeparator="/",
	logAppenders=
	{
		{
			name="console appender",
			type="console",
			level=6
		},
		{
			name="file appender",
			type="file",
			level=6,
			fileName="/tmp/crtmpserver",
			fileHistorySize=10,
			fileLength=1024*256,
			singleLine=true
		}
	},
	applications=
	{
		rootDirectory="applications",
		{
			name="appselector",
			description="Application for selecting the rest of the applications",
			protocol="dynamiclinklibrary",
			validateHandshake=true,
			default=true,
			acceptors = 
			{
				{
					ip="0.0.0.0",
					port=1935,
					protocol="inboundRtmp"
				},
			}
		},
		{
			description="FLV Playback Sample",
			name="flvplayback",
			protocol="dynamiclinklibrary",
			aliases=
			{
			},
			acceptors = 
			{
			},
			externalStreams = 
			{
				{
					uri="rtsp://192.168.1.201/live.sdp",
					localStreamName="Reactor1",
					forceTcp=true
				},
				{
					uri="rtsp://192.168.1.201/live2.sdp",
					localStreamName="Reactor2",
					forceTcp=true
				},
				{
					uri="rtsp://192.168.1.201/live3.sdp",
					localStreamName="Reactor3",
					forceTcp=true
				},
			},
			validateHandshake=true,
			keyframeSeek=true,
			seekGranularity=1.5,
			clientSideBuffer=12,
		},
		--#INSERTION_MARKER# DO NOT REMOVE THIS. USED BY appscaffold SCRIPT.
	}
}

