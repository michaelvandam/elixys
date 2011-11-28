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
				{
					ip="0.0.0.0",
					port=6666,
					protocol="inboundLiveFlv",
					waitForMetadata=true,
				},
				{
					ip="0.0.0.0",
					port=9999,
					protocol="inboundTcpTs"
				},
				--[[{
					ip="0.0.0.0",
					port=7654,
					protocol="inboundRawHttpStream",
					crossDomainFile="/tmp/crossdomain.xml"
				},
				{
					ip="0.0.0.0",
					port=554,
					protocol="inboundRtsp"
				},]]--
			},
			externalStreams = 
			{
				--[[
				{
					uri="rtsp://fms20.mediadirect.ro/live2/realitatea/realitatea",
					localStreamName="rtsp_test",
					forceTcp=true
				},
				{
					uri="rtmp://edge01.fms.dutchview.nl/botr/bunny",
					localStreamName="rtmp_test",
					swfUrl="http://www.example.com/example.swf";
					pageUrl="http://www.example.com/";
					emulateUserAgent="MAC 10,1,82,76",
				}]]--
			},
			validateHandshake=true,
			keyframeSeek=true,
			seekGranularity=1.5,
			clientSideBuffer=12,
		},
		--#INSERTION_MARKER# DO NOT REMOVE THIS. USED BY appscaffold SCRIPT.
	}
}

