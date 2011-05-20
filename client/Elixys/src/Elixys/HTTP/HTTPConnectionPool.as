package Elixys.HTTP
{
	import flash.events.EventDispatcher;
	import flash.utils.ByteArray;
	
	import mx.collections.ArrayList;
	import mx.utils.Base64Encoder;

	public class HTTPConnectionPool extends EventDispatcher
	{
		/***
		 * Public functions
		 **/
		
		// Construction
		public function HTTPConnectionPool(sServer:String, nPort:uint, nMaxConnections:uint)
		{
			// Remember the connection details
			m_sServer = sServer;
			m_nPort = nPort;
			
			// Create our array of connections
			for (var i:uint = 0; i < nMaxConnections; ++i)
			{
				var pHTTPConnection:HTTPConnection = new HTTPConnection(this);
				m_pHTTPConnections.addItem(pHTTPConnection);
			}
		}
		
		// Set and get the user's credentials
		public function SetCredentialsRaw(sUsername:String, sPassword:String):void
		{
			// Encode the username and password using basic authentication
			var pEncoder:Base64Encoder = new Base64Encoder();
			pEncoder.insertNewLines = false;
			pEncoder.encode(sUsername + ":" + sPassword);
			m_sCredentials = pEncoder.toString();
		}
		public function SetCredentials(sCredentials:String):void
		{
			// Remember the credentials
			m_sCredentials = sCredentials;
		}
		public function GetCredentials():String
		{
			// Return the credentials that we have
			return m_sCredentials;
		}
		
		// Get the server and port
		public function GetServer():String
		{
			return m_sServer;
		}
		public function GetPort():uint
		{
			return m_nPort;
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
				pHTTPConnection = m_pHTTPConnections.getItemAt(i) as HTTPConnection;
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
				pHTTPConnection = m_pHTTPConnections.getItemAt(i) as HTTPConnection;
				if (pHTTPConnection.IsAvailable())
				{
					// Send the request
					pHTTPConnection.SendRequest(pHTTPRequest);
					return;
				}
			}
			
			// Everyone is busy.  Store the request in our array so we can send it later
			m_pHTTPRequestQueue.addItem(pHTTPRequest);
		}
	
		// Called by our connections when the complete a request
		public function OnConnectionAvailable(pHTTPConnection:HTTPConnection):void
		{
			// Do we have another request in our queue?
			if (m_pHTTPRequestQueue.length)
			{
				// Yes, so pop it off and submit it
				var pHTTPRequest:HTTPRequest = m_pHTTPRequestQueue.getItemAt(0) as HTTPRequest;
				m_pHTTPRequestQueue.removeItemAt(0);
				pHTTPConnection.SendRequest(pHTTPRequest);
			}
		}
		
		/***
		 * Internal functions
		 **/
		
		/***
		 * Member variables
		 **/
		
		// Static MIME strings
		public static var MIME_FLASH:String = "application/x-shockwave-flash";
		public static var MIME_JSON:String = "application/json";
		public static var MIME_HTML:String = "text/html";
		
		// Connection details
		private var m_sServer:String = "";
		private var m_nPort:uint = 0;
		private var m_sCredentials:String = "";
		
		// Array of connections
		private var m_pHTTPConnections:ArrayList = new ArrayList();

		// Queue of requests waiting to be sent
		private var m_pHTTPRequestQueue:ArrayList = new ArrayList();
	}
}