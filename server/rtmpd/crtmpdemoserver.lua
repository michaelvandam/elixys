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
			},
			externalStreams = 
			{
			},
			validateHandshake=true,
			keyframeSeek=true,
			seekGranularity=1.5,
			clientSideBuffer=12,
		},
		--#INSERTION_MARKER# DO NOT REMOVE THIS. USED BY appscaffold SCRIPT.
	}
}

