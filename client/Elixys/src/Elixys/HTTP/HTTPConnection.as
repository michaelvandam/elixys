package Elixys.HTTP
{
	import Elixys.Events.*;
	
	import flash.events.Event;
	import flash.events.EventDispatcher;
	import flash.events.HTTPStatusEvent;
	import flash.events.IOErrorEvent;
	import flash.events.ProgressEvent;
	import flash.events.SecurityErrorEvent;
	import flash.events.TimerEvent;
	import flash.net.Socket;
	import flash.utils.ByteArray;
	import flash.utils.Dictionary;
	import flash.utils.Timer;
	
	// This class performs normal HTTP operations over a socket.  Yes, it's lame that we need to implement this.  It should
	// be part of Adobe's library, but their version is severly limited in terms of functionality.
	public class HTTPConnection extends EventDispatcher
	{
		/***
		 * Construction
		 **/
		
		public function HTTPConnection(pHTTPConnectionPool:HTTPConnectionPool)
		{
			// Remember the connection pool
			m_pHTTPConnectionPool = pHTTPConnectionPool;
			
			// Add event listeners
			m_pResponseTimer.addEventListener(TimerEvent.TIMER_COMPLETE, OnResponseTimerComplete);
		}

		/***
		 * Public functions
		 **/
		
		// Check the state of the connection
		public function IsConnected():Boolean
		{
			return m_bConnected;
		}
		public function IsAvailable():Boolean
		{
			if (!m_pSocket)
			{
				return true;
			}
			else
			{
				return (!m_pOutstandingRequest);
			}
		}
		
		// Send the request to the server
		public function SendRequest(pHTTPRequest:HTTPRequest):void
		{
			// Make sure there is no outstanding request
			if (!IsAvailable())
			{
				throw new Error("Concurrency error");
			}
			
			// Reset our retry counter and send the request
			m_nRetryCount = 0;
			SendRequestInternal(pHTTPRequest);			
		}

		// Drop any existing connection
		public function DropConnection():void
		{
			// Make sure we are connected
			if (m_bConnected)
			{
				// Stop the response timer, close the socket connection and clear our flag
				m_pResponseTimer.stop();
				try
				{
					m_pSocket.close();
				}
				catch (err:Error)
				{
				}
				m_pSocket = null;
				m_bConnected = false;
				m_bWaitingForResponse = false;
			}
			
			// Clear any outstanding request
			m_pOutstandingRequest = null;
		}
		
		/***
		 * Request sending functions
		 **/
		
		protected function SendRequestInternal(pHTTPRequest:HTTPRequest):void
		{
			try
			{
				// Remember the outstanding request
				m_pOutstandingRequest = pHTTPRequest;

				// Make sure we're connected
				if (!IsConnected())
				{
					// Connnect to the server
					m_pSocket = new Socket();
					m_pSocket.addEventListener(Event.CONNECT, OnSocketConnectEvent);
					m_pSocket.addEventListener(ProgressEvent.SOCKET_DATA, OnSocketProgressEvent);
					m_pSocket.addEventListener(IOErrorEvent.IO_ERROR, OnSocketIOErrorEvent);
					m_pSocket.addEventListener(SecurityErrorEvent.SECURITY_ERROR, OnSocketSecurityErrorEvent);
					m_pSocket.connect(m_pHTTPConnectionPool.Server, m_pHTTPConnectionPool.Port);
					
					// Return and we'll send the request once we connect
					return;
				}
				
				// Create our initial request headers
				var pHeaderArray:Array = new Array();
				pHeaderArray.push("Host: " + m_pHTTPConnectionPool.Server);
				pHeaderArray.push("User-Agent: AdobeAIR");
				pHeaderArray.push("Accept: " + pHTTPRequest.m_sAcceptMIME);
				pHeaderArray.push("Authorization: Basic " + m_pHTTPConnectionPool.Credentials);
				pHeaderArray.push("Connection: Keep-Alive");
				
				// Add post headers
				var sMethod:String = pHTTPRequest.m_sMethod.toUpperCase();
				if (sMethod == "POST")
				{
					if (pHTTPRequest.m_pBody != null)
					{
						pHeaderArray.push("Content-Length: " + pHTTPRequest.m_pBody.bytesAvailable);
					}
					else
					{
						pHeaderArray.push("Content-Length: 0");
					}
					pHeaderArray.push("Content-Type: " + HTTPConnectionPool.MIME_JSON);
				}
				
				// Add the specified request headers
				if (pHTTPRequest.m_pHeaders != null)
				{
					pHeaderArray = pHTTPRequest.m_pHeaders.concat(pHeaderArray);
				}
				
				// Format the request string
				var sRequest:String = sMethod + " " + pHTTPRequest.m_sResource + " HTTP/1.1\r\n";
				sRequest += pHeaderArray.join("\r\n");
				sRequest += "\r\n\r\n";
				
				// Send the request
				for (var i:uint = 0; i < sRequest.length; ++i)
				{
					m_pSocket.writeByte(sRequest.charCodeAt(i));
				}
				
				// Send the body
				if (pHTTPRequest.m_pBody != null)
				{
					m_pSocket.writeBytes(pHTTPRequest.m_pBody);
				}
				
				// Flush the socket
				m_pSocket.flush();

				// Start the response timer and set the response flag
				m_pResponseTimer.start();
				m_bWaitingForResponse = true;
			}
			catch (err:Error)
			{
				// Check for invalid sockets
				if (err.errorID == 2002)
				{
					// This socket has gone bad.  Drop the connection and send the outstanding request again to prompt the creation of a new one
					m_pSocket = null;
					m_bConnected = false;
					SendRequestInternal(m_pOutstandingRequest);
				}
				else
				{
					// Pass an exception event up to our parent
					m_pHTTPConnectionPool.dispatchEvent(new ExceptionEvent("Communication failed"));
				}
			}
		}
		
		// Called when the socket is connected
		protected function OnSocketConnectEvent(event:Event):void
		{
			// Check our connected flag to make sure we only acknowledge this event once
			if (!m_bConnected)
			{
				// Set our flag
				m_bConnected = true;
				
				// Are we sitting on an outstanding request?
				if (m_pOutstandingRequest != null)
				{
					// Yes, so send it
					SendRequestInternal(m_pOutstandingRequest);
				}
				else
				{
					// No, so dispatch the connection event to anyone listening
					m_pHTTPConnectionPool.dispatchEvent(event);
				}				
			}
		}

		/***
		 * Request receiving functions
		 **/
		
		// Called as the socket receives data
		protected function OnSocketProgressEvent(event:ProgressEvent):void
		{
			try
			{
				// Make sure we have data available
				if (!m_pSocket.bytesAvailable)
				{
					return;
				}
				
				// Make sure we're waiting for a response.  We get unexpected responses when we retry a request that is taking too long
				if (!m_bWaitingForResponse)
				{
					// Discard extra responses
					var pDiscardedBytes:ByteArray = new ByteArray();
					m_pSocket.readBytes(pDiscardedBytes);
					return;
				}

				// Stop the timer if it's running
				if (m_pResponseTimer.running)
				{
					m_pResponseTimer.stop();
				}

				// Capture the HTTP response headers if we don't have them yet
				if (!m_nContentLength)
				{
					do
					{
						// Add the next byte to the header
						var nByte:uint = m_pSocket.readByte();
						m_pHTTPResponseHeader.writeByte(nByte);
						
						// Watch for the terminating sequence
						var nNextHeaderByte:uint;
						if ((m_nHTTPResponseHeader == 0) || (m_nHTTPResponseHeader == 2))
						{
							nNextHeaderByte = 0xD;
						}
						else
						{
							nNextHeaderByte = 0xA;
						}
						if (nByte == nNextHeaderByte)
						{
							++m_nHTTPResponseHeader;
						}
						else
						{
							m_nHTTPResponseHeader = 0;
						}
					} while ((m_nHTTPResponseHeader != 4) && m_pSocket.bytesAvailable);
					
					// Return if we don't have the entire header yet
					if (m_nHTTPResponseHeader != 4)
					{
						return;
					}
					
					// Now we have the HTTP response header.  Break the byte array into an array of strings
					m_pHTTPResponseHeaders = m_pHTTPResponseHeader.toString().split("\r\n");
					
					// Extract the status code and content length
					m_nStatusCode = ExtractStatusCode();
					m_nContentLength = ExtractContentLength();
	
					// Inform anyone listening of the status code
					var pHTTPStatusEvent:HTTPStatusEvent = new HTTPStatusEvent(HTTPStatusEvent.HTTP_STATUS, false, false, m_nStatusCode);
					m_pHTTPConnectionPool.dispatchEvent(pHTTPStatusEvent);
				}
			
				// Continue adding the new bytes to the body until we have it all
				if ((m_nContentLength - m_pHTTPResponseBody.bytesAvailable) > m_pSocket.bytesAvailable)
				{
					m_pSocket.readBytes(m_pHTTPResponseBody, m_pHTTPResponseBody.bytesAvailable, m_pSocket.bytesAvailable);
				}
				else
				{
					m_pSocket.readBytes(m_pHTTPResponseBody, m_pHTTPResponseBody.bytesAvailable, m_nContentLength - m_pHTTPResponseBody.bytesAvailable);
				}
	
				// Is this request is complete?
				if (m_pHTTPResponseBody.length == m_nContentLength)
				{
					// Yes.  Dispatch a server responded event if we are retrying a post
					if (m_nRetryCount && (m_pOutstandingRequest.m_sMethod == "POST"))
					{
						var pStatusEvent:StatusEvent = new StatusEvent(StatusEvent.SERVERRESPONDED);
						m_pHTTPConnectionPool.dispatchEvent(pStatusEvent);
					}
					
					// Create and dispatch the response
					var pHTTPResponse:HTTPResponse = new HTTPResponse();
					pHTTPResponse.m_nStatusCode = m_nStatusCode;
					pHTTPResponse.m_pHeaders = m_pHTTPResponseHeaders;
					pHTTPResponse.m_pBody = m_pHTTPResponseBody;
					m_pHTTPConnectionPool.dispatchEvent(new HTTPResponseEvent(pHTTPResponse));

					// Reset our state
					m_pHTTPResponseHeader.clear();
					m_nHTTPResponseHeader = 0;
					m_pHTTPResponseHeaders = null;
					m_nStatusCode = 0;
					m_nContentLength = 0;
					m_pHTTPResponseBody.clear();
					m_pOutstandingRequest = null;
					m_bWaitingForResponse = false;
					
					// Inform the connection pool that we are available
					m_pHTTPConnectionPool.OnConnectionAvailable(this);
				}
			}
			catch (err:Error)
			{
				m_pHTTPConnectionPool.dispatchEvent(new ExceptionEvent("Communication failed"));
			}
		}
		
		// Extract status code from the HTTP response headers
		protected function ExtractStatusCode():uint
		{
			// Scan for the HTTP status code
			for each (var sHeader:String in m_pHTTPResponseHeaders)
			{
				if (sHeader.slice(0, HTTP_STATUS.length) == HTTP_STATUS)
				{
					// Found it.  Extract the code
					return int(sHeader.slice(HTTP_STATUS.length, HTTP_STATUS.length + 3));
				}
			}
			
			// Failed to find HTTP status code
			throw new Error("Corrupt response");
		}
		
		// Extract content length from the HTTP response headers
		protected function ExtractContentLength():uint
		{
			// Scan for the HTTP content length
			for each (var sHeader:String in m_pHTTPResponseHeaders)
			{
				if (sHeader.slice(0, HTTP_CONTENTLENGTH.length) == HTTP_CONTENTLENGTH)
				{
					// Found it.  Extract the content length
					return int(sHeader.slice(HTTP_CONTENTLENGTH.length));
				}
			}
			
			// Failed to find HTTP content length
			throw new Error("Corrupt response");
		}

		/***
		 * Timeout and error functions
		 **/
		
		// Called when the response timer completes
		protected function OnResponseTimerComplete(event:TimerEvent):void
		{
			// Have we exceeded out retry limit?
			if (m_nRetryCount < 10)
			{
				// No, so dispatch a server not responding event and increment our counter
				if ((m_nRetryCount == 0) && (m_pOutstandingRequest.m_sMethod == "POST"))
				{
					var pStatusEvent:StatusEvent = new StatusEvent(StatusEvent.SERVERNOTRESPONDING);
					m_pHTTPConnectionPool.dispatchEvent(pStatusEvent);
				}
				++m_nRetryCount;
			}
			else
			{
				// Give up
				if (m_pOutstandingRequest.m_sMethod == "POST")
				{
					// Send an exception event if we're posting
					var pExceptionEvent:ExceptionEvent = new ExceptionEvent("Server not responding");
					m_pHTTPConnectionPool.dispatchEvent(pExceptionEvent);
				}
				else
				{
					// Reset our state and inform the connection pool that we are available otherwise
					m_pHTTPResponseHeader.clear();
					m_nHTTPResponseHeader = 0;
					m_pHTTPResponseHeaders = null;
					m_nStatusCode = 0;
					m_nContentLength = 0;
					m_pHTTPResponseBody.clear();
					m_pOutstandingRequest = null;
					m_bWaitingForResponse = false;
					m_pHTTPConnectionPool.OnConnectionAvailable(this);
				}
			}
		}

		// Called when a socket IO or security error occurs
		protected function OnSocketIOErrorEvent(event:IOErrorEvent):void
		{
			var pExceptionEvent:ExceptionEvent = new ExceptionEvent("Connection failed");
			m_pHTTPConnectionPool.dispatchEvent(pExceptionEvent);
		}		
		protected function OnSocketSecurityErrorEvent(event:SecurityErrorEvent):void
		{
			var pExceptionEvent:ExceptionEvent = new ExceptionEvent("Connection failed");
			m_pHTTPConnectionPool.dispatchEvent(pExceptionEvent);
		}

		/***
		 * Member variables
		 **/
		
		// Connection pool
		protected var m_pHTTPConnectionPool:HTTPConnectionPool;
						
		// Socket classes
		protected var m_pSocket:Socket = null;
		protected var m_bConnected:Boolean = false;

		// HTTP response
		protected var m_pHTTPResponseHeader:ByteArray = new ByteArray();
		protected var m_nHTTPResponseHeader:uint = 0;
		protected var m_pHTTPResponseHeaders:Array = null;
		protected var m_nStatusCode:uint = 0;
		protected var m_nContentLength:uint = 0;
		protected var m_pHTTPResponseBody:ByteArray = new ByteArray();
		protected var m_bWaitingForResponse:Boolean = false;

		// Response timer, outstanding HTTP request and retry count
		protected var m_pResponseTimer:Timer = new Timer(1000, 1);
		protected var m_pOutstandingRequest:HTTPRequest;
		protected var m_nRetryCount:uint;
			
		// Static HTTP strings
		protected static var HTTP_STATUS:String = "HTTP/1.1 ";
		protected static var HTTP_CONTENTLENGTH:String = "Content-Length: ";
	}
}
