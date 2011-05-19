package Elixys
{
	import flash.events.Event;
	import flash.utils.ByteArray;
	
	// This custom event is used to return an HTTP response to the holder of the HTTP connection
	public class HTTPResponseEvent extends Event
	{
		// Constructor
		public function HTTPResponseEvent(pHTTPResponse:HTTPResponse, bBubbles:Boolean = false, bCancelable:Boolean = false)
		{
			m_pHTTPResponse = pHTTPResponse;
			super(HTTPRESPONSE, bubbles, cancelable);
		}
		
		// Event name
		static public var HTTPRESPONSE:String = "HTTPResponseEvent";
		
		// HTTP response
		public var m_pHTTPResponse:HTTPResponse;
	}
}
