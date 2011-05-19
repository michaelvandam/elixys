package Elixys
{
	import flash.utils.ByteArray;

	public class HTTPResponse
	{
		// Construction
		public function HTTPResponse()
		{
		}
		
		// Data members
		public var m_nStatusCode:uint = 0;
		public var m_pHeaders:Array;
		public var m_pBody:ByteArray;
	}
}