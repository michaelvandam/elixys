package Elixys.Objects
{
	import flash.utils.flash_proxy;
	
	public class ComponentActivity extends Component
	{
		// Constructor
		public function ComponentActivity(data:String = null, existingcontent:Object = null)
		{
			// Call the base constructor
			if ((data == null) && (existingcontent == null))
			{
				data = m_sDefault;
			}
			super(data, existingcontent);
			
			// Validate the object type
			if ((ComponentType != null) && (ComponentType != TYPE))
			{
				throw new Error("State object mismatch");
			}
		}

		// Type
		static public var TYPE:String = "ACTIVITY";

		// Default format
		private var m_sDefault:String = "{ \"type\":\"component\", \"componenttype\":\"ACTIVITY\", \"name\":\"\", \"componentid\":\"\", " +
			"\"sequenceid\":\"\", \"reactor\":\"\", \"reactordescription\":\"\", \"reactorvalidation\":\"\" }";
	}
}
