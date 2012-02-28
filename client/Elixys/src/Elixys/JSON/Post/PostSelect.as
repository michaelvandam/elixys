package Elixys.JSON.Post
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class PostSelect extends JSONObject
	{
		// Constructor
		public function PostSelect()
		{
			// Call the base constructor
			super(m_sDefault);
		}
		
		// Data wrappers
		public function set Type(value:String):void
		{
			super.flash_proxy::getProperty("action").type = value;
		}
		public function set TargetID(value:String):void
		{
			super.flash_proxy::getProperty("action").targetid = value;
		}
		public function set SequenceID(value:uint):void
		{
			super.flash_proxy::setProperty("sequenceid", value);
		}
		
		// Default format
		private var m_sDefault:String = "{" +
			"\"action\":" +
			"{" +
				"\"type\":\"\"," +
				"\"targetid\":\"\"" + 
			"}," +
			"\"sequenceid\":0}";
	}
}
