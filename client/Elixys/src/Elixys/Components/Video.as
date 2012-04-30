package Elixys.Components
{
	import fl.core.UIComponent;
	
	import flash.display.DisplayObject;
	import flash.display.Sprite;
	import flash.events.NetStatusEvent;
	import flash.events.TimerEvent;
	import flash.media.Video;
	import flash.net.NetConnection;
	import flash.net.NetStream;
	import flash.utils.Timer;
	
	// This tab bar component is an extension of the UI component class
	public class Video extends UIComponent
	{
		/***
		 * Construction
		 **/

		public function Video()
		{
			// Call the base constructor
			super();
			
			// Create timers
			m_pWatchTimer = new Timer(250);
			m_pHiddenTimer = new Timer(3000, 1);
			m_pReconnectTimer = new Timer(1000, 1);
			
			// Add event listeners
			m_pWatchTimer.addEventListener(TimerEvent.TIMER, OnWatchTimer);
			m_pHiddenTimer.addEventListener(TimerEvent.TIMER_COMPLETE, OnHiddenTimerComplete);
			m_pReconnectTimer.addEventListener(TimerEvent.TIMER_COMPLETE, OnReconnectTimerComplete);
			
			// Start the watch timer
			m_pWatchTimer.start();
		}
		
		/***
		 * Member functions
		 **/
	
		// Update the video stream URL
		public function SetStream(sRootURL:String, sStreamName:String, nWidth:uint, nHeight:uint):void
		{
			// Has the stream changed?
			if (!m_pVideo || (m_sRootURL != sRootURL) || (m_sStreamName != sStreamName))
			{
				// Yes, so remember the new values
				m_sRootURL = sRootURL;
				m_sFullURL = "rtmp://" + sRootURL + "/flvplayback/";
				m_sStreamName = sStreamName;
	
				// Establish a connection to the server
				CreateVideoConnection();
			}
		}
	
		// Establishes a connection to the server
		protected function CreateVideoConnection():void
		{
			// Drop any existing video connection
			DropVideoConnection();

			// Create the video and net connection
			m_pVideo = new flash.media.Video();
			addChild(m_pVideo);
			m_pNetConnection = new NetConnection();
			m_pNetConnection.addEventListener(NetStatusEvent.NET_STATUS, OnNetConnection);
			m_pNetConnection.client = {};
			m_pNetConnection.client.onBWDone = OnBWDone;
			m_pNetConnection.connect(m_sFullURL);
					
			// Bandwidth handler
			function OnBWDone():void
			{
			}
		}
	
		// Drops any existing video connection to the server
		protected function DropVideoConnection():void
		{
			if (m_pVideo != null)
			{
				removeChild(m_pVideo);
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
				
		// Checks the visibilty of the object.  An object is visible if it an all its parents are visible
		protected function CheckVisibility(pDisplayObject:DisplayObject):Boolean
		{
			if (!pDisplayObject.visible)
			{
				return false;
			}
			if ((pDisplayObject.parent != null) && (pDisplayObject.parent is DisplayObject))
			{
				return CheckVisibility(pDisplayObject.parent as DisplayObject);
			}
			return true;
		}
				
		// Updates the video dimensions
		protected function UpdateVideoDimensions():void
		{
			// Resize and center the video
			var fUIComponent:Number = (parent.width * parent.scaleX) / (parent.height * parent.scaleY);
			var fVideo:Number = m_pVideo.width / m_pVideo.height;
			if (fUIComponent < fVideo)
			{
				m_pVideo.height = m_pVideo.height * (width / m_pVideo.width);
				m_pVideo.width = width;
				m_pVideo.y = (height - m_pVideo.height) / 2;
			}
			else if (fUIComponent > fVideo)
			{
				m_pVideo.width = m_pVideo.width * (height / m_pVideo.height);
				m_pVideo.height = height;
				m_pVideo.x = (width - m_pVideo.width) / 2;
			}
			m_nWidth = width;
			m_nHeight = height;
		}
				
		/***
		 * Message handlers
		 **/
	
		protected function OnNetConnection(event:NetStatusEvent):void
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
					// Update the video dimensions
					UpdateVideoDimensions();
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
	
		protected function OnNetStatus(event:NetStatusEvent):void
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
	
		// Called when the watch timer triggers
		protected function OnWatchTimer(event:TimerEvent):void
		{
			// Ignore unless we have a video
			if (m_pVideo == null)
			{
				return;
			}
			
			// Check if we've been shown or hidden
			var bVisible:Boolean = CheckVisibility(this);
			if (bVisible && !m_bVisible)
			{
				// We've been shown.  Stop the hidden timer if it's running
				if (m_pHiddenTimer.running)
				{
					m_pHiddenTimer.stop();
				}
						
				// Recreate the video connection if we're not playing
				if (!m_bPlaying)
				{
					CreateVideoConnection();
				}
			}
			else if (!bVisible && m_bVisible)
			{
				// We've been hidden.  Start the hidden timer
				m_pHiddenTimer.start();
			}
			m_bVisible = bVisible;
	
			// Check if our dimensions have changed
			if ((m_nWidth != width) || (m_nHeight != height))
			{
				UpdateVideoDimensions();
			}
		}
	
		// Called when the hidden timer completes
		protected function OnHiddenTimerComplete(event:TimerEvent):void
		{
			// Drop the video connection
			DropVideoConnection();
		}
	
		// Called when the reconnect timer completes
		protected function OnReconnectTimerComplete(event:TimerEvent):void
		{
			// Recreate the video connection
			CreateVideoConnection();
		}
	
		/***
		 * Member variables
		 **/
				
		// Stream URLs and name
		protected var m_sRootURL:String = "";
		protected var m_sFullURL:String = "";
		protected var m_sStreamName:String = "";
	
		// Video, net connection and stream
		protected var m_pVideo:flash.media.Video;
		protected var m_pNetConnection:NetConnection;
		protected var m_pNetStream:NetStream;
		
		// Timers
		protected var m_pWatchTimer:Timer;
		protected var m_pHiddenTimer:Timer;
		protected var m_pReconnectTimer:Timer;
				
		// Flags and dimensions
		protected var m_bVisible:Boolean = true;
		protected var m_bPlaying:Boolean = false;
		protected var m_nWidth:Number = 0;
		protected var m_nHeight:Number = 0;
	}
}
