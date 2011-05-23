package Elixys.Objects
{
	
	import flash.utils.flash_proxy;
	
	public class PostPrompt extends JSONObject
	{
		// Constructor
		public function PostPrompt()
		{
			// Call the base constructor
			super(m_sDefault);
		}
		
		// Data wrappers
		public function TargetID(targetID:String):void
		{
			super.flash_proxy::getProperty("action").targetid = targetID;
		}
		public function Edit1(edit1:String):void
		{
			super.flash_proxy::setProperty("edit1", edit1);
		}
		public function Edit2(edit2:String):void
		{
			super.flash_proxy::setProperty("edit2", edit2);
		}
		
		// Default format
		private var m_sDefault:String = "{ \"action\":{ \"type\":\"BUTTONCLICK\", \"targetid\":\"\"	}, \"edit1\":\"\", \"edit2\":\"\" }";
	}
}
