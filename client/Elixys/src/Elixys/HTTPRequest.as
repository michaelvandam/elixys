package Elixys
{
	import flash.utils.ByteArray;

	public class HTTPRequest
	{
		// Construction
		public function HTTPRequest()
		{
		}

		// Data members
		public var m_sMethod:String = "";
		public var m_sResource:String = "";
		public var m_sAcceptMIME:String = "";
		public var m_pHeaders:Array;
		public var m_pBody:ByteArray;
	}
}
