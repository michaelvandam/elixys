configuration=
{
	daemon=false,
	pathSeparator="/",
	logAppenders=
	{
		{
			name="console appender",
			type="coloredConsole",
			level=6
		},
		{
			name="file appender",
			type="file",
			level=6,
			fileName="/tmp/crtmpserver.log"
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
				"simpleLive",
				"vod",
				"live",
				"WeeklyQuest",
				"SOSample",
				"oflaDemo",
			},
			acceptors = 
			{
				{
					ip="0.0.0.0",
					port=1935,
					protocol="inboundRtmfp"
				},
				{
					ip="0.0.0.0",
					port=554,
					protocol="inboundRtsp"
				}
			},
			externalStreams = 
			{
				-- {
				-- 	uri="rtsp://127.0.0.1:5544/ch=0",
				-- 	localStreamName="teststream"
				-- },
			},
			validateHandshake=true,
			keyframeSeek=true,
			seekGranularity=1.5, --in seconds, between 0.1 and 600
			clientSideBuffer=12, --in seconds, between 5 and 30
		},
		--#INSERTION_MARKER# DO NOT REMOVE THIS. USED BY appscaffold SCRIPT.
	}
}

