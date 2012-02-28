package Elixys.HTTP
{
	import com.flex.Base64Encoder;

	import flash.events.EventDispatcher;
	import flash.utils.ByteArray;
	
	public class HTTPConnectionPool extends EventDispatcher
	{
		/***
		 * Construction
		 **/
		
		public function HTTPConnectionPool(nMaxConnections:uint)
		{
			// Create our array of connections
			for (var i:uint = 0; i < nMaxConnections; ++i)
			{
				var pHTTPConnection:HTTPConnection = new HTTPConnection(this);
				m_pHTTPConnections.push(pHTTPConnection);
			}
		}

		/***
		 * Member functions
		 **/

		// Set and get the server
		public function set Server(value:String):void
		{
			m_sServer = value;
		}
		public function get Server():String
		{
			return m_sServer;
		}

		// Set and get the port
		public function set Port(value:uint):void
		{
			m_nPort = value;
		}
		public function get Port():uint
		{
			return m_nPort;
		}

		// Set and get the user's credentials
		public function SetRawCredentials(sUsername:String, sPassword:String):void
		{
			// Encode the username and password using basic authentication
			var pEncoder:Base64Encoder = new Base64Encoder();
			pEncoder.insertNewLines = false;
			pEncoder.encode(sUsername + ":" + sPassword);
			m_sCredentials = pEncoder.toString();
		}
		public function get Credentials():String
		{
			return m_sCredentials;
		}
		
		// Send the request to the server
		public function SendRequestA(sMethod:String, sResource:String, sAcceptMIME:String, pHeaders:Array = null, pBody:ByteArray = null):void
		{
			// Wrap the parameters in an HTTPRequest object
			var pHTTPRequest:HTTPRequest = new HTTPRequest();
			pHTTPRequest.m_sMethod = sMethod;
			pHTTPRequest.m_sResource = sResource;
			pHTTPRequest.m_sAcceptMIME = sAcceptMIME;
			pHTTPRequest.m_pHeaders = pHeaders;
			pHTTPRequest.m_pBody = pBody;

			// Call the other function
			SendRequestB(pHTTPRequest);
		}
		public function SendRequestB(pHTTPRequest:HTTPRequest):void
		{
			// Scan our connections for one that is connected and available
			var pHTTPConnection:HTTPConnection, i:uint;
			for (i = 0; i < m_pHTTPConnections.length; ++i)
			{
				// Check connectivity and availability
				pHTTPConnection = m_pHTTPConnections[i] as HTTPConnection;
				if (pHTTPConnection.IsConnected() && pHTTPConnection.IsAvailable())
				{
					// Send the request
					pHTTPConnection.SendRequest(pHTTPRequest);
					return;
				}
			}
			
			// Scan our connections for one that is available
			for (i = 0; i < m_pHTTPConnections.length; ++i)
			{
				// Check availability
				pHTTPConnection = m_pHTTPConnections[i] as HTTPConnection;
				if (pHTTPConnection.IsAvailable())
				{
					// Send the request
					pHTTPConnection.SendRequest(pHTTPRequest);
					return;
				}
			}
			
			// Everyone is busy.  Store the request in our array so we can send it later
			m_pHTTPRequestQueue.push(pHTTPRequest);
		}
		
		// Drops all open connections to the server
		public function DropAllConnections():void
		{
			// Drop each connection
			var pHTTPConnection:HTTPConnection, i:uint;
			for (i = 0; i < m_pHTTPConnections.length; ++i)
			{
				pHTTPConnection = m_pHTTPConnections[i] as HTTPConnection;
				pHTTPConnection.DropConnection();
			}
		}
	
		// Called by our connections when the complete a request
		public function OnConnectionAvailable(pHTTPConnection:HTTPConnection):void
		{
			// Do we have another request in our queue?
			if (m_pHTTPRequestQueue.length)
			{
				// Yes, so pop it off and submit it
				var pHTTPRequest:HTTPRequest = m_pHTTPRequestQueue[0] as HTTPRequest;
				m_pHTTPRequestQueue = m_pHTTPRequestQueue.slice(1);
				pHTTPConnection.SendRequest(pHTTPRequest);
			}
		}
		
		/***
		 * Member variables
		 **/
		
		// Static MIME strings
		public static var MIME_FLASH:String = "application/x-shockwave-flash";
		public static var MIME_JSON:String = "application/json";
		public static var MIME_HTML:String = "text/html";
		
		// Connection details
		protected var m_sServer:String = "";
		protected var m_nPort:uint = 80;
		protected var m_sCredentials:String = "";
		
		// Array of connections
		protected var m_pHTTPConnections:Array = new Array();

		// Queue of requests waiting to be sent
		protected var m_pHTTPRequestQueue:Array = new Array();
	}
}