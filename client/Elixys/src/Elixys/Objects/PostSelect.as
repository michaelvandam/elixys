package Elixys.Objects
{
	
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
		public function Type(type:String):void
		{
			super.flash_proxy::getProperty("action").type = type;
		}
		public function TargetID(targetID:String):void
		{
			super.flash_proxy::getProperty("action").targetid = targetID;
		}
		public function SequenceID(sequenceID:uint):void
		{
			super.flash_proxy::setProperty("sequenceid", sequenceID);
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
