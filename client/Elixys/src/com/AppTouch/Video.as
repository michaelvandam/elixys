package com.AppTouch
{
	import flash.display.DisplayObjectContainer;
	import flash.events.Event;
	import flash.events.EventDispatcher;
	import flash.events.NetStatusEvent;
	import flash.events.TimerEvent;
	import flash.media.Video;
	import flash.net.NetConnection;
	import flash.net.NetStream;
	import flash.utils.Timer;
	
	// This class implements the default AppTouch video player
	public class Video extends VideoBase
	{
		/***
		 * Constructor
		 **/
		
		public function Video()
		{
			m_sDebugOut += "Default video constructor\n";
			
			// Create reconnect timer
			m_pReconnectTimer = new Timer(1000, 1);
			m_pReconnectTimer.addEventListener(TimerEvent.TIMER_COMPLETE, OnReconnectTimerComplete);
		}

		/***
		 * VideoBase function overrides
		 **/
		
		// Establishes a video connection to the server
		public override function CreateVideoConnection(sStreamURL:String, sStreamName:String):void
		{
			// Drop any existing video connection
			DropVideoConnection();
			
			// Remember the URL
			m_sStreamURL = sStreamURL;
			m_sStreamName = sStreamName;
			
			// Create the video and net connection
			m_pVideo = new flash.media.Video();
			m_pParent.addChild(m_pVideo);
			m_pNetConnection = new NetConnection();
			m_pNetConnection.addEventListener(NetStatusEvent.NET_STATUS, OnNetConnection);
			m_pNetConnection.client = {};
			m_pNetConnection.client.onBWDone = OnBWDone;
			m_pNetConnection.connect(m_sStreamURL);
			
			// Bandwidth handler
			function OnBWDone():void
			{
			}
		}
		
		// Drops any existing video connection to the server
		public override function DropVideoConnection():void
		{
			if (m_pVideo != null)
			{
				m_pParent.removeChild(m_pVideo);
			}
			if (m_pNetConnection != null)
			{
				m_pNetConnection.close();
			}
			if (m_pNetStream != null)
			{
				m_pNetStream.close();
			}
			m_pVideo = null;
			m_pNetConnection = null;
			m_pNetStream = null;
			m_bPlaying = false;
		}
		
		// Returns the width and height of the video
		public override function GetVideoWidth():uint
		{
			return m_nVideoWidth;
		}
		public override function GetVideoHeight():uint
		{
			return m_nVideoHeight;
		}
		
		// Sets the size of the video
		public override function SetVideoPosition(nX:int, nY:int, nWidth:uint, nHeight:uint):void
		{
			m_pVideo.x = nX;
			m_pVideo.y = nY;
			m_pVideo.width = nWidth;
			m_pVideo.height = nHeight;
		}
		
		/***
		 * Message handlers
		 **/
		
		private function OnNetConnection(event:NetStatusEvent):void
		{
			if (event.info.code == "NetConnection.Connect.Success")
			{
				// Create the net stream and play the stream
				m_pNetStream = new NetStream(m_pNetConnection);
				m_pNetStream.client = {};
				m_pNetStream.client.onMetaData = OnMetaData;
				m_pNetStream.bufferTime = 0;
				m_pNetStream.play(m_sStreamName);
				m_pVideo.attachNetStream(m_pNetStream);
				m_pNetStream.addEventListener(NetStatusEvent.NET_STATUS, OnNetStatus);
				
				// Metadata handler
				function OnMetaData(item:Object):void
				{
					// Inform any listeners that our video dimensions have changed
					m_nVideoWidth = item.width;
					m_nVideoHeight = item.height;
					dispatchEvent(new Event(VIDEO_RESIZE));
				}
			}
			else if((event.info.code == "NetConnection.Connect.Closed") || (event.info.code == "NetConnection.Connect.Failed"))
			{
				// Make sure we're visible
				if (m_bVisible)
				{
					// We can't call connect from here so set the reconnect timer
					m_pReconnectTimer.start();
				}
			}
		}
		
		private function OnNetStatus(event:NetStatusEvent):void
		{
			// Set the playing flag
			if (event.info.code == "NetStream.Play.Start")
			{
				m_bPlaying = true;
			}
			if (event.info.code == "NetStream.Play.Stop")
			{
				m_bPlaying = false;
			}
			
			// Check for the end of the video stream (stop followed by empty)
			if (!m_bPlaying && (event.info.code == "NetStream.Buffer.Empty"))
			{
				m_pNetStream.play(m_sStreamName);
			}
		}
		
		// Called when the reconnect timer completes
		private function OnReconnectTimerComplete(event:TimerEvent):void
		{
			// Recreate the video connection
			CreateVideoConnection(m_sStreamURL, m_sStreamName);
		}
		
		/***
		 * Member variables
		 **/
		
		// URL and name of the stream
		private var m_sStreamURL:String;
		private var m_sStreamName:String;
		
		// Video, net connection and stream
		private var m_pVideo:flash.media.Video;
		private var m_pNetConnection:NetConnection;
		private var m_pNetStream:NetStream;
		
		// Video dimensions
		private var m_nVideoWidth:uint = 0;
		private var m_nVideoHeight:uint = 0;
		
		// Reconnect timer
		private var m_pReconnectTimer:Timer;
	}
}
