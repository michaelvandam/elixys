package Elixys.JSON.Post
{
	import Elixys.JSON.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class PostHome extends JSONObject
	{
		// Constructor
		public function PostHome()
		{
			// Call the base constructor
			super(m_sDefault);
		}
		
		// Data wrappers
		public function set TargetID(value:String):void
		{
			super.flash_proxy::getProperty("action").targetid = value;
		}

		// Default format
		private var m_sDefault:String = "{ \"action\": { \"type\":\"BUTTONCLICK\", \"targetid\":\"\" } }";
	}
}
