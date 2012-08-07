package Elixys.Components
{
	import com.AppTouch.Video;
	
	import fl.core.UIComponent;
	
	import flash.display.DisplayObject;
	import flash.display.Sprite;
	import flash.events.Event;
	import flash.events.NetStatusEvent;
	import flash.events.TimerEvent;
	import flash.net.NetConnection;
	import flash.net.NetStream;
	import flash.utils.Timer;
	
	// This video component is an extension of the UI component class
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
			
			// Grab the appropriate implementation
			m_pVideo = new com.AppTouch.Video();
			m_pVideo.SetParent(this);
			m_pVideo.addEventListener(VideoBase.VIDEO_RESIZE, OnVideoResize);
			
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
			
			// Update the video dimensions
			UpdateVideoDimensions();
		}
	
		// Establishes a connection to the server
		protected function CreateVideoConnection():void
		{
			// Drop any existing video connection
			DropVideoConnection();

			// Create the video and net connection
			m_pVideo.CreateVideoConnection(m_sFullURL, m_sStreamName);
		}
	
		// Drops any existing video connection to the server
		protected function DropVideoConnection():void
		{
			m_pVideo.DropVideoConnection();
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
			var fUIComponent:Number = width / height;
			var nCurrentWidth:uint = m_pVideo.GetVideoWidth();
			var nCurrentHeight:uint = m_pVideo.GetVideoHeight();
			if (nCurrentWidth && nCurrentHeight)
			{
				var nNewWidth:uint = 0, nNewHeight:uint = 0;
				var nX:int = 0, nY:int = 0;
				var fVideo:Number = nCurrentWidth / nCurrentHeight;
				if (fUIComponent < fVideo)
				{
					nNewHeight = nCurrentHeight * (width / nCurrentWidth);
					nNewWidth = width;
					nY = (height - nNewHeight) / 2;
				}
				else if (fUIComponent > fVideo)
				{
					nNewWidth = nCurrentWidth * (height / nCurrentHeight);
					nNewHeight = height;
					nX = (width - nNewWidth) / 2;
				}
				m_pVideo.SetVideoPosition(nX, nY, nNewWidth, nNewHeight);
			}
				
			// Remember our new size
			m_nWidth = width;
			m_nHeight = height;
		}
				
		/***
		 * Message handlers
		 **/
	
		// Called when the watch timer triggers
		protected function OnWatchTimer(event:TimerEvent):void
		{
			// Ignore unless we have a video
			if (m_pVideo == null)
			{
				return;
			}
			
			// Check if we've been shown or hidden
			/*
			var bVisible:Boolean = CheckVisibility(this);
			if (bVisible && !m_bVisible)
			{
				// We've been shown.  Stop the hidden timer if it's running
				trace("A");
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
				trace("B");
				// We've been hidden.  Start the hidden timer
				m_pHiddenTimer.start();
			}
			m_bVisible = bVisible;
			*/
			
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
	
		// Called when the video size updates
		protected function OnVideoResize(event:Event):void
		{
			// Resize the video
			UpdateVideoDimensions();
		}

		/***
		 * Member variables
		 **/
		
		// Video implementation
		protected var m_pVideo:com.AppTouch.Video;

		// Stream URLs and name
		protected var m_sRootURL:String = "";
		protected var m_sFullURL:String = "";
		protected var m_sStreamName:String = "";
	
		// Source video dimensions
		protected var m_nVideoWidth:int = 0;
		protected var m_nVideoHeight:int = 0;
		
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
