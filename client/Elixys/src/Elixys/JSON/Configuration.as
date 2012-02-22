package Elixys.JSON
{
	
	import flash.utils.flash_proxy;
	
	public class Configuration extends JSONObject
	{
		// Constructor
		public function Configuration(data:String, existingcontent:Object = null)
		{
			// Call the base constructor
			super(data, existingcontent);
			
			// Validate the object type
			if ((Type != null) && (Type != TYPE))
			{
				throw new Error("Object type mismatch");
			}
		}
		
		// Static type
		public static function get TYPE():String
		{
			return "configuration";
		}
		
		// Data wrappers
		public function get Name():String
		{
			return super.flash_proxy::getProperty("name");
		}
		public function get Version():String
		{
			return super.flash_proxy::getProperty("version");
		}
		public function get Debug():Boolean
		{
			var sDebug:String = super.flash_proxy::getProperty("version");
			return (sDebug == "true");
		}
		public function get SupportedOperations():Array
		{
			return super.flash_proxy::getProperty("supportedoperations");
		}
		public function get Reactors():uint
		{
			return super.flash_proxy::getProperty("reactors");
		}
		public function get ReagentsPerReactor():uint
		{
			return super.flash_proxy::getProperty("reagentsperreactor");
		}
		public function get ColumnsPerReactor():uint
		{
			return super.flash_proxy::getProperty("columnsperreactor");
		}
	}
}