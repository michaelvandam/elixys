package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class PostView extends JSONObject
	{
		// Constructor
		public function PostView()
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
