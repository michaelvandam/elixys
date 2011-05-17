package Elixys.Objects
{
	import Elixys.JSONObject;
	
	import flash.utils.flash_proxy;
	
	public class Configuration extends JSONObject
	{
		// Constructor
		public function Configuration(data:String = null)
		{
			// Call the base constructor
			super(data);
			
			// Validate the object type
			if (data != null)
			{
				if (Type() != TYPE)
				{
					throw new Error("Object type mismatch");
				}
			}
		}
		
		// Data wrappers
		public function Type():String
		{
			return super.flash_proxy::getProperty("type");
		}
		public function Name():String
		{
			return super.flash_proxy::getProperty("name");
		}
		public function Version():String
		{
			return super.flash_proxy::getProperty("version");
		}
		public function Debug():Boolean
		{
			var sDebug:String = super.flash_proxy::getProperty("version");
			return (sDebug == "true");
		}
		public function SupportedOperations():Array
		{
			return super.flash_proxy::getProperty("supportedoperations");
		}
		
		// Type
		static public var TYPE:String = "configuration";
	}
}