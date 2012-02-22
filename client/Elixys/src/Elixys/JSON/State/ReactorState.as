package Elixys.JSON.State
{
	import Elixys.JSON.JSONObject;

	import flash.utils.flash_proxy;
	
	public class ReactorState extends JSONObject
	{
		// Constructor
		public function ReactorState(data:String, existingcontent:Object = null)
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
			return "reactorstate";
		}

		// Data wrappers
		public function get ReactorNumber():uint
		{
			return super.flash_proxy::getProperty("number");
		}
		public function get Temperature():Number
		{
			return super.flash_proxy::getProperty("temperature");
		}
		public function get Position():ReactorPosition
		{
			// Parse the reactor position
			if (m_pReactorPosition == null)
			{
				m_pReactorPosition = new ReactorPosition(null, super.flash_proxy::getProperty("position"));
			}
			return m_pReactorPosition;
		}
		public function get Activity():Number
		{
			return super.flash_proxy::getProperty("activity");
		}
		public function get ActivityTime():String
		{
			return super.flash_proxy::getProperty("activitytime");
		}
		public function get TransferPosition():String
		{
			return super.flash_proxy::getProperty("transferposition");
		}
		public function get StirSpeed():uint
		{
			return super.flash_proxy::getProperty("stirspeed");
		}
		public function get Video():String
		{
			return super.flash_proxy::getProperty("video");
		}
		public function get ColumnPosition():String
		{
			return super.flash_proxy::getProperty("columnposition");
		}
		
		// State components
		private var m_pReactorPosition:ReactorPosition = null;
	}
}
