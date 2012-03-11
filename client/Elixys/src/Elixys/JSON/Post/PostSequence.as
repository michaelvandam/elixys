package Elixys.JSON.Post
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class PostSequence extends JSONObject
	{
		// Constructor
		public function PostSequence()
		{
			// Call the base constructor
			super(m_sDefault);
		}
		
		// Data wrappers
		public function set TargetID(targetID:String):void
		{
			super.flash_proxy::getProperty("action").targetid = targetID;
		}

		// Default format
		private var m_sDefault:String = "{" +
			"\"action\":" +
			"{" +
				"\"type\":\"BUTTONCLICK\"," +
				"\"targetid\":\"\"" +
			"}}";
	}
}
