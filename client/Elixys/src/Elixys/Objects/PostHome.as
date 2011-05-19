package Elixys.Objects
{
	import Elixys.JSONObject;
	
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
		public function TargetID(targetID:String):void
		{
			super.flash_proxy::getProperty("action").targetid = targetID;
		}

		// Default format
		private var m_sDefault:String = "{ \"action\": { \"type\":\"BUTTONCLICK\", \"targetid\":\"\" } }";
	}
}
