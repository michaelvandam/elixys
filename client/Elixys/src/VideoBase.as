package
{
	import flash.display.DisplayObjectContainer;
	import flash.events.EventDispatcher;

	public class VideoBase extends EventDispatcher
	{
		// Temp
		public function VideoBase()
		{
			m_sDebugOut += "VideoBase constructor\n";
		}
		
		/***
		 * Member functions
		 **/
		
		// Sets the parent
		public function SetParent(pParent:DisplayObjectContainer):void
		{
			m_pParent = pParent;
		}
		
		// Called when the visibility of the parent changes
		public function OnParentVisibility(bVisible:Boolean):void
		{
			m_bVisible = bVisible;
		}
		
		// Establishes a video connection to the server
		public function CreateVideoConnection(sStreamURL:String, sStreamName:String):void
		{
		}
		
		// Drops any existing video connection to the server
		public function DropVideoConnection():void
		{
		}

		// Returns if the stream is playing
		public function IsPlaying():Boolean
		{
			return m_bPlaying;
		}

		// Returns the width and height of the video
		public function GetVideoWidth():uint
		{
			return 0;
		}
		public function GetVideoHeight():uint
		{
			return 0;
		}
		
		// Sets the size of the video
		public function SetVideoPosition(nX:int, nY:int, nWidth:uint, nHeight:uint):void
		{
		}
		
		// Temp
		protected var m_sDebugOut:String = "";
		public function GetDebugOut():String
		{
			return m_sDebugOut;
		}
		
		/***
		 * Member variables
		 **/
		
		// Video resize event
		public static var VIDEO_RESIZE:String = "VideoResize";

		// Parent
		protected var m_pParent:DisplayObjectContainer;

		// Flags
		protected var m_bPlaying:Boolean = false;
		protected var m_bVisible:Boolean = true;
	}
}