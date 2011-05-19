package Elixys
{
	import flash.events.Event;
	import flash.utils.ByteArray;
	
	// This custom event is used to pass an HTTP request to the holder of the HTTP connection
	public class HTTPRequestEvent extends Event
	{
		// Constructor
		public function HTTPRequestEvent(pHTTPRequest:HTTPRequest, bBubbles:Boolean = false, bCancelable:Boolean = false)
		{
			m_pHTTPRequest = pHTTPRequest;
			super(HTTPREQUEST, bubbles, cancelable);
		}
		
		// Event name
		static public var HTTPREQUEST:String = "HTTPRequestEvent";
		
		// HTTP request
		public var m_pHTTPRequest:HTTPRequest;
	}
}
